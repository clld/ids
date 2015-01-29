<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>Words in ${h.link(request, ctx.language)} for meaning ${ctx.parameter.id} "${h.link(request, ctx.parameter)}"</h2>

<table class="table table-nonfluid">
% if ctx.language.dictionary.default_representation:
    <thead>
        <tr>
            <td>${ctx.language.dictionary.default_representation}</td>
            % if ctx.language.dictionary.alt_representation:
           <td>${ctx.language.dictionary.alt_representation}</td>
            % endif
        </tr>
    </thead>
% endif
    <tbody>
% for i, value in enumerate(ctx.values):
    <tr>
        <td>${h.link(request, value.word, class_='charissil')}</td>
        % if ctx.language.dictionary.alt_representation:
        <td class="charissil">${value.word.alt_name or ''}</td>
        % endif
    </tr>
% endfor
    </tbody>
</table>
% if ctx.comment:
<h3>Comment</h3>
<p>${ctx.comment}</p>
% endif
<%def name="sidebar()">
<div class="well well-small">
<dl>
    <dt class="contribution">${_('Contribution')}:</dt>
    <dd class="contribution">
        ${h.link(request, ctx.contribution)}
        by
        ${h.linked_contributors(request, ctx.contribution)}
        ${h.cite_button(request, ctx.contribution)}
    </dd>
    <dt class="parameter">${_('Parameter')}:</dt>
    <dd class="parameter">${h.link(request, ctx.parameter)}</dd>
</dl>
</div>
</%def>
