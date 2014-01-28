<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<%def name="sidebar()">
    <div style="margin-top: 5px;">
    ${util.codes(ctx.language)}
    </div>
    <br clear="both" />
    <%util:well title="Compiler">
        ${h.linked_contributors(request, ctx)}
        ${h.cite_button(request, ctx)}
    </%util:well>
    % if ctx.language.latitude is not None:
    <%util:well>
        ${request.map.render()}
        ${h.format_coordinates(ctx.language)}
    </%util:well>
    % endif
    % if ctx.language.sources:
    <%util:well title="Sources">
        ${util.sources_list(sorted(list(ctx.language.sources), key=lambda s: s.name))}
    </%util:well>
    % endif
</%def>

<h2>${ctx.name} Dictionary</h2>

% if ctx.jsondatadict['status'] == '1':
<div class="alert alert-info">in progress</div>
% endif

${request.get_datatable('values', h.models.Value, contribution=ctx).render()}
