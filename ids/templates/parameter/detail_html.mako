<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} "${ctx.name}"</%block>

<h2>${_('Parameter')} "${ctx.name}"</h2>

${util.dl_table(*[('chapter', ctx.chapter.name)], **{k: getattr(ctx, k) for k in 'french russian spanish portugese'.split()})}

${request.map.render()}

${request.get_datatable('values', h.models.Value, parameter=ctx).render()}
