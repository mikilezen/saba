# Reusing verification evidence

After a content or base change, rerun checks whose supporting assumptions changed or whose relevance is uncertain. Unrelated changes do not require repeating all verification or review. Carry evidence forward with the intervening diff, the contract it proved, and the reason that contract is unaffected. Consider shared dependencies and configuration, not just overlapping files.

Evaluate PR review and required CI against the current remote head. Inherited evidence retains its original identity and an explanation of its applicability; it is not a fresh execution. Keep raw verification artifacts outside tracked source files.

## Per-file commits

When the user authorizes commits, create one separate commit for each changed file. Never combine changes from multiple files into one commit. Stage only the file for the current commit, use a concise message that describes that file's change, and push only when the user requests it.
