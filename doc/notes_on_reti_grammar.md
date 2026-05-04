# Notes on RETI Grammar

This note explains the parser generation error that occurred in [`vendor/tree-sitter-reti/grammar.js`](/home/areo/Documents/Studium/PicoC-Compiler/vendor/tree-sitter-reti/grammar.js:30).

The relevant rule is:

```js
block: $ => prec.right(seq(
  field('label', $.label),
  ':',
  repeat($.directive),
  repeat($.statement),
)),
```

## Full Error Message

Running `tree-sitter generate` produced:

```text
Error: Error when generating parser

Caused by:
    Unresolved conflict for symbol sequence:

      label  ':'  •  'LOAD'  …

    Possible interpretations:

      1:  (block  label  ':'  •  block_repeat2)
      2:  (block  label  ':')  •  'LOAD'  …

    Possible resolutions:

      1:  Specify a left or right associativity in `block`
      2:  Add a conflict for these rules: `block`
```

## What the Error Means

The dot marks the parser position. At that point, Tree-sitter has already read `label:` and the next token is `LOAD`.

The grammar allows two valid interpretations:

1. `LOAD` is the first `statement` inside the current `block`.
2. The `block` ends immediately after `label:`, and `LOAD` starts the next top-level `statement`.

Tree-sitter shows that as:

```text
1: (block  label  ':'  •  block_repeat2)
2: (block  label  ':')  •  'LOAD'
```

`block_repeat2` is Tree-sitter's internal name for one of the `repeat(...)` parts of the rule.

## Why the Grammar Is Ambiguous

The ambiguity comes from these two parts:

```js
repeat($.directive),
repeat($.statement),
```

Both `repeat(...)` expressions may match zero items. That means `label:` is already a complete `block`, even if nothing follows it.

But if the next token is `LOAD`, that token can also start a valid `statement`, so Tree-sitter cannot decide whether to:

```text
finish the block now
```

or

```text
keep parsing the current block
```

## Shift and Reduce in a Bottom-Up Parser

Tree-sitter uses a bottom-up parsing strategy. A bottom-up parser reads tokens from left to right and tries to build larger grammar nodes from smaller pieces that it has already recognized.

Two important actions in that process are:

- `shift`: consume the next input token and keep building the current construct
- `reduce`: take tokens or subtrees that are already recognized and collapse them into a completed grammar rule

At the point

```text
label  ':'  •  'LOAD'
```

the parser has already recognized `label:`. Since both `repeat($.directive)` and `repeat($.statement)` may be empty, `label:` is already enough to reduce to a complete `block`.

So one valid action is:

- `reduce` now: treat `label:` as a finished `block`

But `LOAD` can also start a valid `statement` inside that same `block`, so another valid action is:

- `shift` `LOAD`: keep parsing and make it part of the current `block`

This is the inner reason for the conflict: the parser has both a valid reduce action and a valid shift action at the same point.

In parser terminology, this is a shift/reduce conflict. The grammar does not make it clear whether the parser should finish the current `block` immediately or continue extending it.

## Why `prec.right` Fixes It

`prec.right(...)` resolves this ambiguity by telling Tree-sitter to prefer the interpretation that continues to the right when both parses are otherwise valid.

In practice, that means:

- do not close the `block` too early
- if the next token can belong to the current `block`, prefer that parse

So for:

```text
label: LOAD ...
```

Tree-sitter will prefer:

```text
one block containing LOAD
```

instead of:

```text
an empty block followed by a separate statement
```

Viewed in terms of bottom-up parsing, `prec.right` tells Tree-sitter how to break the tie:

- prefer `shift` over `reduce` here
- keep consuming input for the current `block` when that is still legal

So `prec.right` does not change what the grammar can express. It tells the parser which valid interpretation to choose when both are possible.

## Intuition

This is a common Tree-sitter ambiguity pattern:

- a rule can end early because it contains `repeat(...)` or `optional(...)`
- the next token could either extend that rule or begin the next construct

`prec.right` is a compact way of saying:

```text
if possible, keep this construct open and attach the following token to it
```
