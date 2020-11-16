<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} "${ctx.name}"</%block>

<h2>${_('Parameter')} ${ctx.id} "${ctx.name}"</h2>

<p><b>Concepticon:</b> ${ctx.concepticon_link(request)}</p>
<p><b>IDS Chapter ${ctx.chapter.id}:</b> ${h.link(request, ctx.chapter)}</p>

${util.dl_table(**{k.title(): getattr(ctx, k) for k in 'french russian spanish portuguese'.split()})}

${request.map.render()}

${request.get_datatable('values', h.models.Value, parameter=ctx).render()}
