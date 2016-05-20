<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "chapters" %>

<h2>Chapter ${ctx.id}: ${ctx.name}</h2>

${request.get_datatable('parameters', h.models.Parameter, chapter=ctx).render()}
