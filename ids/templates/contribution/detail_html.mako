<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! from ids.models import ROLES %>
<%! active_menu_item = "contributions" %>

<%def name="sidebar()">
    <div style="margin-top: 5px;">
    ${util.codes(ctx.language)}
    </div>
    <br clear="both" />
    <%util:well>
        <dl>
        % for id, label in ROLES.items():
            <% contribs = [ca.contributor for ca in ctx.contributor_assocs if ca.ord == id] %>
            % if contribs:
            <dt>${label}</dt>
            <dd>
                <ul${' class="unstyled"' if len(contribs) == 1 else ''|n}>
                % for c in contribs:
                    <li>${h.link(request, c)}</li>
                % endfor
                </ul>
            </dd>
            % endif
        % endfor
        </dl>
        ${h.cite_button(request, ctx)}
    </%util:well>
    % if ctx.language.latitude is not None:
    <%util:well>
        ${request.map.render()}
        ${h.format_coordinates(ctx.language)}
    </%util:well>
    % endif
    % if ctx.references:
    <%util:well title="Sources">
        ${util.sources_list(sorted([a.source for a in ctx.references], key=lambda s: s.name))}
    </%util:well>
    % endif
</%def>

<h2>${ctx.name} Dictionary</h2>
${h.alt_representations(request, ctx, doc_position='left', exclude=['md.html'])}

% if ctx.jsondata['status'] == '1':
<div class="alert alert-info">in progress</div>
% endif

${request.get_datatable('values', h.models.Value, contribution=ctx).render()}
