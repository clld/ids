<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>Words in ${h.link(request, ctx.language)} for meaning "${h.link(request, ctx.parameter)}"</h2>

<ul class="unstyled">
% for i, value in enumerate(ctx.values):
    <li>
        ${h.link(request, value.word, class_='charissil')}
        % if ctx.description:
        (${ctx.description})
        % endif
        ;
        % if value.word.alt_name:
        <span class="charissil">${value.word.alt_name}</span>
        % if ctx.alt_description:
        (${value.word.alt_description})
        % endif
        ;
        % endif
    </li>
% endfor
</ul>
% if ctx.jsondatadict.get('alt_representation'):
<h3>${ctx.jsondatadict['alt_representation'][0]} representation</h3>
<p>${ctx.jsondatadict['alt_representation'][1]}</p>
% endif
% if ctx.jsondatadict['comment']:
<h3>Comment</h3>
<p>${ctx.jsondatadict['comment']}</p>
% endif
<%def name="sidebar()">
<div class="well well-small">
<dl>
    <dt class="contribution">${_('Contribution')}:</dt>
    <dd class="contribution">
        ${h.link(request, ctx.contribution)}
        by
        ${h.linked_contributors(request, ctx.contribution)}
        ${h.button('cite', onclick=h.JSModal.show(ctx.contribution.name, request.resource_url(ctx.contribution, ext='md.html')))}
    </dd>
    <dt class="parameter">${_('Parameter')}:</dt>
    <dd class="parameter">${h.link(request, ctx.parameter)}</dd>
</dl>
</div>
</%def>
