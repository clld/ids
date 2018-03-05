<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>${ctx}</title>
    <link href="${request.url}"/>
    <updated>${h.datetime.datetime.now().isoformat()}</updated>
    <author>${request.dataset.name}</author>
    <id>${request.url}</id>
    <!-- Not available. -->
</feed>
