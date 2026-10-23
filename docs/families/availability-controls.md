            # Availability controls

            Bounds expensive work, queue growth, retries, and failure isolation for exposed operations.

            ## Reviewed subjects

            - search request
- report build
- file conversion
- batch import
- webhook delivery
- background job
- authentication request
- export request
- notification fanout

            ## Control themes

            - sets a work limit
- uses bounded retry behavior
- isolates failure domains

            Each rule requires explicit offline evidence. A rule definition adds report context and does not initiate a scan or execute supplied reproduction text.
