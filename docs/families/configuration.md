            # Configuration

            Reviews production defaults, debug behavior, secret sources, and environment separation.

            ## Reviewed subjects

            - application runtime
- web server
- worker process
- scheduled job
- administration console
- object storage client
- database client
- message consumer
- report generator

            ## Control themes

            - uses a production-safe default
- keeps diagnostic detail private
- loads secrets from an approved source

            Each rule requires explicit offline evidence. A rule definition adds report context and does not initiate a scan or execute supplied reproduction text.
