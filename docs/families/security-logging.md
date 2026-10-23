            # Security logging

            Captures actionable security events without leaking credentials or excess personal data.

            ## Reviewed subjects

            - login event
- authorization denial
- administrator action
- credential change
- data export
- configuration change
- integration failure
- rate-limit event
- scope violation

            ## Control themes

            - records the decision context
- excludes secret material
- resists unauthorized alteration

            Each rule requires explicit offline evidence. A rule definition adds report context and does not initiate a scan or execute supplied reproduction text.
