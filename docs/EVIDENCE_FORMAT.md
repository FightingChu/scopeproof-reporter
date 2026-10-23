# Evidence format

An evidence JSON object requires `id`, `rule_id`, `asset`, `observed_at`, `status`, `summary`, `observation`, `reproduction`, and `confidence`. Optional `request` and `response` strings carry sanitized protocol excerpts.

Status is one of `confirmed`, `not-observed`, or `needs-review`. Confidence is `low`, `medium`, or `high`. Timestamps use ISO 8601. Reproduction is an ordered string array. The application treats every string as data and never executes commands embedded in the record.

Assets must exactly match an entry in the scope manifest. This keeps similarly named hosts from being silently merged. Evidence IDs must be unique within one report compilation.
