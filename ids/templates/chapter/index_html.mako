<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! from ids.models import Chapter %>
<%! active_menu_item = "chapters" %>
<%block name="title">${_('Chapters')}</%block>

<h2>Chapters</h2>

${request.get_datatable('chapters', Chapter).render()}
