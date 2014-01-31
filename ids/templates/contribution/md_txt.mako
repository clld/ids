${' and '.join(c.name for c in list(ctx.primary_contributors))}. ${request.dataset.published.year if request.dataset.published else ctx.updated.year}. ${ctx.name} dictionary.
In: ${request.dataset.formatted_editors()|n} (eds.)
${request.dataset.description}.
${request.dataset.publisher_place}: ${request.dataset.publisher_name}.
(Available online at http://${request.dataset.domain}${request.resource_path(ctx)}, Accessed on ${h.datetime.date.today()}.)
