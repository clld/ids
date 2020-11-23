<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%block name="title">Word "${ctx}"</%block>

<h2>Word <span class="charissil">${ctx}</span></h2>

% if ctx.alt_name and ctx.alt_description:
${util.dl_table(**{ctx.alt_description: ctx.alt_name})}
% endif

<h3>Meanings</h3>
<ul>
% for i, value in enumerate(ctx.counterparts):
    <li>${h.link(request, value.valueset.parameter)}</li>
% endfor
</ul>

<%def name="sidebar()">
<div class="well well-small">
<dl>
    <dt class="contribution">Language:</dt>
    <dd class="contribution">
        ${h.link(request, ctx.language)}
    </dd>
</dl>
</div>
</%def>
