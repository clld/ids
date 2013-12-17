<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%block name="title">${_('Contributions')}</%block>

<h2>${_('Contributions')}</h2>
<% m = request.registry.queryUtility(h.interfaces.IMap, 'languages'); m = m(ctx, request) %>
${m.render()}

<div>
    ${ctx.render()}
</div>
