//! Pure-Rust bitcoin script parser.
//!
//! Produces, for every opcode in a script, its mnemonic and its byte offset
//! into the serialised script. The offsets are what the debugger feeds to
//! `tx_engine`'s `Context.ip_start` / `Context.ip_limit`, which index the
//! serialised byte string rather than a token list, so they have to match the
//! script's on-the-wire encoding exactly.
//!
//! Byte order: bitcoin script numbers are little-endian, sign-and-magnitude
//! (the high bit of the most significant byte is the sign). Hex literals are
//! written most-significant-nibble first and are copied verbatim into the
//! script, so their length in bytes is simply half their digit count.

use core::fmt;
use pest::Parser;
use pest_derive::Parser;

#[derive(Parser)]
#[grammar = "script.pest"]
pub struct ScriptParser;

/// An opcode and its byte offset into the serialised script.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OpcodeInfo {
    pub opcode: String,
    pub position: usize,
}

impl fmt::Display for OpcodeInfo {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "OpCode: {}, Position: {}", self.opcode, self.position)
    }
}

/// Everything that can go wrong while parsing.
#[derive(Debug)]
pub enum ParseError {
    /// The input is not valid script.
    Grammar(Box<pest::error::Error<Rule>>),
    /// The script is longer than `usize::MAX` bytes, so an offset overflowed.
    OffsetOverflow,
    /// The grammar produced a rule the walker does not know about. This is a
    /// bug in this crate (grammar and walker out of step), not bad input.
    UnexpectedRule(String),
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::Grammar(e) => write!(f, "failed to parse script: {e}"),
            ParseError::OffsetOverflow => write!(f, "script byte offset overflowed usize"),
            ParseError::UnexpectedRule(r) => {
                write!(f, "internal error: unhandled grammar rule {r}")
            }
        }
    }
}

impl std::error::Error for ParseError {}

impl From<pest::error::Error<Rule>> for ParseError {
    fn from(e: pest::error::Error<Rule>) -> Self {
        ParseError::Grammar(Box::new(e))
    }
}

/// Number of bytes a decimal script number occupies once serialised,
/// including its push prefix.
///
/// Follows bitcoin's minimal encoding:
///  * `0` is `OP_0` and `-1` is `OP_1NEGATE`, one byte each;
///  * `1..=16` are `OP_1`..`OP_16`, one byte each;
///  * anything else is a little-endian sign-and-magnitude byte string with an
///    extra `0x00` appended when the top byte would otherwise collide with the
///    sign bit, preceded by a push opcode.
///
/// `digits` must be a non-empty run of ASCII digits (the grammar guarantees
/// this); `negative` carries the sign separately. Arbitrary precision is
/// handled by dividing the decimal string down rather than going through a
/// fixed-width integer, so a literal wider than 64 or 128 bits is still sized
/// correctly instead of silently failing to parse.
fn serialised_len_of_integer(digits: &str, negative: bool) -> Result<usize, ParseError> {
    let magnitude = decimal_to_le_bytes(digits);

    // OP_0 / OP_1..OP_16 / OP_1NEGATE are single-byte opcodes.
    if magnitude.is_empty() {
        return Ok(1); // zero, however many leading zeros were written
    }
    if magnitude.len() == 1 {
        let v = magnitude[0];
        if !negative && (1..=16).contains(&v) {
            return Ok(1);
        }
        if negative && v == 1 {
            return Ok(1);
        }
    }

    // A trailing byte with the sign bit already set needs a spare byte so the
    // sign is not read as part of the magnitude.
    let needs_sign_byte = magnitude.last().is_some_and(|last| last & 0x80 != 0);
    let payload = magnitude
        .len()
        .checked_add(usize::from(needs_sign_byte))
        .ok_or(ParseError::OffsetOverflow)?;

    // Push prefix: a bare length byte up to 75, then OP_PUSHDATA1/2/4.
    let prefix = match payload {
        0..=75 => 1,
        76..=255 => 2,
        256..=65535 => 3,
        _ => 5,
    };
    payload
        .checked_add(prefix)
        .ok_or(ParseError::OffsetOverflow)
}

/// Convert a decimal digit string to its minimal little-endian byte magnitude.
/// Returns an empty vector for zero. Uses schoolbook long division by 256 so
/// the width of the literal is not bounded by any primitive integer type.
fn decimal_to_le_bytes(digits: &str) -> Vec<u8> {
    // Working copy as individual digit values, most significant first.
    let mut work: Vec<u8> = digits.bytes().map(|b| b - b'0').collect();
    let mut out = Vec::new();

    while work.iter().any(|&d| d != 0) {
        let mut remainder: u16 = 0;
        for digit in work.iter_mut() {
            // remainder < 256 and digit < 10, so this stays well inside u16.
            let acc = remainder * 10 + u16::from(*digit);
            *digit = (acc / 256) as u8;
            remainder = acc % 256;
        }
        out.push(remainder as u8);
        // Drop leading zeros so the loop terminates in O(digits) iterations.
        let first_significant = work.iter().position(|&d| d != 0).unwrap_or(work.len());
        work.drain(..first_significant);
    }
    out
}

/// Number of bytes the hex digits of a `0x...` literal occupy. The grammar
/// guarantees an even, non-zero number of ASCII hex digits, so the division is
/// exact and the byte length equals half the digit count.
fn serialised_len_of_hex(hex_digits: &str) -> usize {
    debug_assert!(hex_digits.len().is_multiple_of(2) && !hex_digits.is_empty());
    hex_digits.len() / 2
}

fn walk(
    pair: pest::iterators::Pair<Rule>,
    byte_offset: &mut usize,
    opcodes: &mut Vec<OpcodeInfo>,
) -> Result<(), ParseError> {
    let advance = |byte_offset: &mut usize, n: usize| -> Result<(), ParseError> {
        *byte_offset = byte_offset
            .checked_add(n)
            .ok_or(ParseError::OffsetOverflow)?;
        Ok(())
    };

    match pair.as_rule() {
        Rule::script | Rule::statement | Rule::if_statement => {
            for inner in pair.into_inner() {
                walk(inner, byte_offset, opcodes)?;
            }
        }
        Rule::opcode | Rule::if_token | Rule::else_token | Rule::endif_token => {
            opcodes.push(OpcodeInfo {
                opcode: pair.as_str().trim().to_string(),
                position: *byte_offset,
            });
            advance(byte_offset, 1)?;
        }
        Rule::data => {
            let text = pair.as_str();
            let len = match text.strip_prefix("0x") {
                Some(hex_digits) => serialised_len_of_hex(hex_digits),
                None => {
                    let (negative, digits) = match text.strip_prefix('-') {
                        Some(d) => (true, d),
                        None => (false, text),
                    };
                    serialised_len_of_integer(digits, negative)?
                }
            };
            advance(byte_offset, len)?;
        }
        Rule::EOI => {}
        other => return Err(ParseError::UnexpectedRule(format!("{other:?}"))),
    }
    Ok(())
}

/// Parse a script and return each opcode with its byte offset.
///
/// Data pushes advance the offset but are deliberately not reported: the
/// debugger indexes breakpoints by operation, and a push is not an operation
/// you can usefully break on.
pub fn parse_script(script_str: &str) -> Result<Vec<OpcodeInfo>, ParseError> {
    let mut parse_result = ScriptParser::parse(Rule::script, script_str)?;
    // `Rule::script` is anchored with SOI/EOI, so a successful parse always
    // yields exactly one pair.
    let script_pair = match parse_result.next() {
        Some(pair) => pair,
        None => return Ok(Vec::new()),
    };

    let mut opcodes = Vec::new();
    let mut byte_offset = 0usize;
    walk(script_pair, &mut byte_offset, &mut opcodes)?;
    Ok(opcodes)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ops(src: &str) -> Vec<(String, usize)> {
        parse_script(src)
            .unwrap_or_else(|e| panic!("{src:?} should parse: {e}"))
            .into_iter()
            .map(|o| (o.opcode, o.position))
            .collect()
    }

    fn names(src: &str) -> Vec<String> {
        ops(src).into_iter().map(|(n, _)| n).collect()
    }

    #[test]
    fn opcodes_that_are_prefixes_of_others_are_not_shadowed() {
        // Each of these used to parse as a shorter opcode plus a stray integer,
        // or fail outright.
        for op in [
            "OP_NOP1",
            "OP_RESERVED1",
            "OP_RESERVED2",
            "OP_VERIF",
            "OP_VERNOTIF",
            "OP_LESSTHANOREQUAL",
            "OP_GREATERTHANOREQUAL",
            "OP_LSHIFTNUM",
            "OP_RSHIFTNUM",
            "OP_SUBSTR",
            "OP_1NEGATE",
            "OP_EQUALVERIFY",
            "OP_NUMEQUALVERIFY",
            "OP_CHECKSIGVERIFY",
            "OP_CHECKMULTISIGVERIFY",
            "OP_CHECKLOCKTIMEVERIFY",
            "OP_CHECKSEQUENCEVERIFY",
            "OP_IFDUP",
            "OP_16",
            // OP_NOP10 is the awkward one: OP_NOP1 is a prefix of it, and
            // OP_NOP is a prefix of both.
            "OP_NOP",
            "OP_NOP9",
            "OP_NOP10",
        ] {
            assert_eq!(names(op), vec![op.to_string()], "mis-parsed {op}");
        }
    }

    /// Every opcode the grammar names must parse to exactly itself.
    ///
    /// The list is read out of `script.pest` rather than written here, so an
    /// opcode added to the grammar is covered the moment it is added and this
    /// test cannot fall behind.
    ///
    /// This is the check that makes shadowing impossible to reintroduce. Both
    /// of the original grammar bugs were one opcode sitting before a longer
    /// one it is a prefix of -- `OP_NOP` before `OP_NOP1`, `OP_VER` before
    /// `OP_VERIF` -- and each was found by hand, one at a time. Ordering is
    /// still the fix; this is what notices when the ordering is wrong.
    #[test]
    fn every_opcode_in_the_grammar_parses_to_exactly_itself() {
        let grammar = include_str!("script.pest");

        // The opcode literals are written `^"OP_..."`, case-insensitive
        // strings. Anything else in the file is not an opcode name.
        let mut names_in_grammar: Vec<&str> = Vec::new();
        for (index, _) in grammar.match_indices("^\"OP_") {
            let rest = &grammar[index + 2..];
            if let Some(end) = rest.find('"') {
                names_in_grammar.push(&rest[..end]);
            }
        }
        names_in_grammar.sort_unstable();
        names_in_grammar.dedup();

        assert!(
            names_in_grammar.len() > 100,
            "only found {} opcode literals in the grammar; the extraction is \
             probably broken rather than the grammar being small",
            names_in_grammar.len()
        );

        // The four branch tokens are not standalone opcodes: `OP_IF` on its own
        // is an unterminated `if_statement`, and refusing it is correct. They
        // are covered as complete constructs in `conditionals` below, and by
        // the assertion underneath this loop that each really is in the
        // grammar -- so excluding them here cannot hide one going missing.
        const BRANCH_TOKENS: [&str; 4] = ["OP_IF", "OP_NOTIF", "OP_ELSE", "OP_ENDIF"];

        let mut shadowed = Vec::new();
        for op in names_in_grammar
            .iter()
            .filter(|o| !BRANCH_TOKENS.contains(o))
        {
            match parse_script(op) {
                Ok(parsed) => {
                    let got: Vec<&str> = parsed.iter().map(|o| o.opcode.as_str()).collect();
                    if got != vec![*op] {
                        shadowed.push(format!("{op} parsed as {got:?}"));
                    }
                }
                Err(_) => shadowed.push(format!("{op} did not parse at all")),
            }
        }
        assert!(
            shadowed.is_empty(),
            "{} of {} opcodes do not parse to themselves:\n  {}",
            shadowed.len(),
            names_in_grammar.len(),
            shadowed.join("\n  ")
        );

        // The exclusion above is only safe while these are genuinely present.
        for token in BRANCH_TOKENS {
            assert!(
                names_in_grammar.contains(&token),
                "{token} has gone from the grammar and the sweep was skipping it"
            );
        }
    }

    /// OP_NOP4..OP_NOP8 are absent on purpose, not by accident.
    ///
    /// Genesis reclaimed those slots in BSV, so they are aliases rather than
    /// no-ops: OP_NOP4 is OP_SUBSTR, OP_NOP5 is OP_LEFT, OP_NOP6 is OP_RIGHT,
    /// OP_NOP7 is OP_LSHIFTNUM, OP_NOP8 is OP_RSHIFTNUM. Each is accepted
    /// under the name it actually does something as; the OP_NOPn spelling is
    /// rejected so a script cannot be written in one mnemonic and printed back
    /// in another. Change this deliberately if aliases are wanted.
    #[test]
    fn genesis_reclaimed_nop_slots_are_named_for_what_they_do() {
        for real in [
            "OP_SUBSTR",
            "OP_LEFT",
            "OP_RIGHT",
            "OP_LSHIFTNUM",
            "OP_RSHIFTNUM",
        ] {
            assert_eq!(names(real), vec![real.to_string()]);
        }
        for alias in ["OP_NOP4", "OP_NOP5", "OP_NOP6", "OP_NOP7", "OP_NOP8"] {
            assert!(
                parse_script(alias).is_err(),
                "{alias} is a BSV alias and should be rejected, not silently \
                 accepted as something else"
            );
        }
    }

    #[test]
    fn unknown_word_is_an_error_not_a_partial_match() {
        // `OP_DUPLICATE` must not be accepted as `OP_DUP` + `LICATE`.
        assert!(parse_script("OP_DUPLICATE").is_err());
        assert!(parse_script("OP_NOP99").is_err());
    }

    #[test]
    fn conditionals() {
        assert_eq!(names("OP_IF OP_ENDIF"), ["OP_IF", "OP_ENDIF"]);
        assert_eq!(
            names("OP_NOTIF OP_1 OP_ENDIF"),
            ["OP_NOTIF", "OP_1", "OP_ENDIF"]
        );
        assert_eq!(
            names("OP_IF OP_1 OP_ELSE OP_2 OP_ELSE OP_3 OP_ENDIF"),
            ["OP_IF", "OP_1", "OP_ELSE", "OP_2", "OP_ELSE", "OP_3", "OP_ENDIF"]
        );
        assert_eq!(
            names("OP_1 OP_IF OP_2 OP_IF OP_3 OP_ELSE OP_8 OP_ENDIF OP_4 OP_ENDIF OP_5"),
            [
                "OP_1", "OP_IF", "OP_2", "OP_IF", "OP_3", "OP_ELSE", "OP_8", "OP_ENDIF", "OP_4",
                "OP_ENDIF", "OP_5"
            ]
        );
        // An unmatched OP_ENDIF is not script.
        assert!(parse_script("OP_ENDIF").is_err());
    }

    #[test]
    fn offsets_follow_the_serialised_encoding() {
        assert_eq!(
            ops("OP_1 OP_2 OP_ADD"),
            [("OP_1".into(), 0), ("OP_2".into(), 1), ("OP_ADD".into(), 2)]
        );
        // 0x02fb09 is a 3-byte push; OP_EQUALVERIFY therefore lands at 6.
        assert_eq!(
            ops("0x02fb09 0x02fb09 OP_EQUALVERIFY"),
            [("OP_EQUALVERIFY".into(), 6)]
        );
        // OP_PUSHDATA1(1) + 0x03(1) + 0x010203(3) = 5, so OP_ADD is at 5.
        assert_eq!(
            ops("OP_PUSHDATA1 0x03 0x010203 OP_ADD"),
            [("OP_PUSHDATA1".into(), 0), ("OP_ADD".into(), 5)]
        );
    }

    #[test]
    fn decimal_integers_are_sized_by_minimal_encoding() {
        // (literal, serialised byte count) taken from the reference encoding:
        // small values collapse to a single opcode, everything else is a
        // length-prefixed little-endian magnitude with a sign byte if needed.
        for (literal, expected) in [
            ("0", 1),     // OP_0
            ("1", 1),     // OP_1
            ("16", 1),    // OP_16
            ("-1", 1),    // OP_1NEGATE
            ("17", 2),    // 0x01 0x11
            ("127", 2),   // 0x01 0x7f
            ("128", 3),   // 0x02 0x80 0x00  (sign byte)
            ("255", 3),   // 0x02 0xff 0x00
            ("256", 3),   // 0x02 0x00 0x01
            ("32767", 3), // 0x02 0xff 0x7f
            ("32768", 4), // 0x03 0x00 0x80 0x00
            ("-2", 2),    // 0x01 0x82
            ("-127", 2),  // 0x01 0xff
            ("-128", 3),  // 0x02 0x80 0x80
            ("2555", 3),
            ("100000", 4),
            ("1000000", 4),
        ] {
            let got = ops(&format!("{literal} OP_ADD"));
            assert_eq!(
                got,
                [("OP_ADD".to_string(), expected)],
                "wrong size for literal {literal}"
            );
        }
    }

    #[test]
    fn integers_wider_than_a_primitive_are_still_sized() {
        // 2^64 needs 9 magnitude bytes; the top byte is 0x01 so no sign byte,
        // plus a 1-byte push prefix.
        assert_eq!(ops("18446744073709551616 OP_ADD"), [("OP_ADD".into(), 10)]);
        // 2^255 needs 32 magnitude bytes with the top bit set, so 33 payload
        // bytes plus the prefix.
        let two_pow_255 =
            "57896044618658097711785492504343953926634992332820282019728792003956564819968";
        assert_eq!(
            ops(&format!("{two_pow_255} OP_ADD")),
            [("OP_ADD".into(), 34)]
        );
    }

    #[test]
    fn odd_length_hex_is_rejected_rather_than_truncated() {
        assert!(parse_script("0xaabbc").is_err());
        assert!(parse_script("0xaabb").is_ok());
        assert!(parse_script("0x").is_err());
    }

    #[test]
    fn comments_and_whitespace() {
        assert_eq!(names("OP_1 /* ignored */ OP_2"), ["OP_1", "OP_2"]);
        assert_eq!(names("OP_1 // ignored\nOP_2"), ["OP_1", "OP_2"]);
        assert_eq!(names("\tOP_1\r\n  OP_2\n"), ["OP_1", "OP_2"]);
    }

    #[test]
    fn opcodes_are_case_insensitive_but_reported_verbatim() {
        assert_eq!(names("op_dup"), ["op_dup"]);
    }

    #[test]
    fn empty_script_parses_to_nothing() {
        assert_eq!(names(""), Vec::<String>::new());
    }

    #[test]
    fn errors_do_not_panic() {
        assert!(parse_script("NOT_AN_OPCODE").is_err());
        assert!(parse_script("OP_IF OP_1").is_err());
        assert!(parse_script("\u{1F600}").is_err());
    }
}
