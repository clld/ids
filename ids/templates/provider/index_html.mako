<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! from ids.models import Provider %>
<%! active_menu_item = "providers" %>
<%block name="title">${_('Providers')}</%block>

<h2>${_('Providers')}</h2>

${request.get_datatable('providers', Provider).render()}
