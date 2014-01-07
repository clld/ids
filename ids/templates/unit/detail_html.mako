<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>Word "${ctx}"</h2>

<h3>Meanings</h3>
<ul class="unstyled">
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
