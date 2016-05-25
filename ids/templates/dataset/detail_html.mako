<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>


<%def name="sidebar()">
    <%util:well>
        ${h.newline2br(h.text_citation(request, ctx))|n}
        ${h.cite_button(request, ctx)}
    </%util:well>
</%def>

<div style="text-align: center">
<h1>${ctx.description}</h1>

<p class="lead">
    <em>Founding Editor:</em><br/>
    †Mary Ritchie Key<br/>
    <em>General Editor:</em><br/>
    Bernard Comrie
</p>
</div>

<%util:section title="Purpose" id="Purpose" level="4">
    The Intercontinental Dictionary Series (IDS) is a database where lexical material across
    the languages of the world is organized in such a way that comparisons can be made.
    Historical and comparative studies and theoretical linguistic research can be based on
    this documentation. The IDS was conceived of by Mary Ritchie Key (University of
    California, Irvine) in the 1980s as a
    long-term cooperative project that will go on for the next generation or so and will
    involve linguists all over the world. It is aimed towards international understanding
    and cooperation. This is a pioneering effort that will have global impact. The purpose
    also contributes to preserving information on the little-known and "non-prestigious"
    languages of the world, many of which are becoming extinct.
</%util:section>

<%util:section title="Rationale" id="Rationale" level="4">
    Information on languages of the world is scattered over all the continents and islands
    and published in dozens of languages and scripts. There is need of a database where one
    can find comparable material to formulate hypotheses and test and validate those theories.
    For example, theories on intercontinental connections have been proposed on the basis of
    the distribution of 'sweet potato' and yet there is no single source where words with this
    meaning can be found in many languages. Good quantitative and statistical studies are
    almost impossible to do now in non-Western languages. The IDS will provide a quantitative
    base for a scientific approach to language analysis and comparison. The IDS will provide
    the research tools necessary for expanding studies such as phonological theory, word
    formation, language change, lexical distribution, symbolism and onomatopoeia, language
    classification, and other ideas that have to do with history of people and migrations.
    The IDS will serve not only as a synonym dictionary (or cross-linguistic thesaurus) but
    as an index to meaning and to cultures of various peoples around the earth.
</%util:section>

<%util:section title="Plan of Series" id="PlanofSeries" level="4">
    The IDS wordlists appear as a series of digital, freely accessible, freely downloadable,
    and freely usable wordlists (CC-BY license).
</%util:section>

<%util:section title="Procedure" id="Procedure" level="4">
    The IDS is developed in cooperation and complementation with other research projects.
    Throughout the world there are linguistic activities from establishing databases in
    universities and think-tanks to publishing grammar series and literacy materials, to
    individual projects such as dictionaries of single languages. Many projects seek to make
    linguistic data accessible in a format that will allow generalizations to be made. Recent
    developments now give us the potential for tying together linguistic databases. The IDS
    aims to be part of these activities.
</%util:section>

<%util:section title="Format" id="Format" level="4">
    Each wordlist has been produced in the same format, which assures the cross-linguistic
    comparability. Comparative work in Indo-European has been carried on for over 200 years,
    and excellent research tools have been produced. This experience forms a basis for similar
    research tools to be produced for the pre-literate languages that have been more recently
    recorded. Specifically, a model for IDS is <em>A Dictionary of Selected Synonyms in the
    Principal Indo-European Languages</em>, compiled
    ${h.link(request, buck1949, label="by Carl Darling Buck")}.
    The dictionary is organized in a topical outline of
    <a href="${request.route_url('chapters')}">${chapters} chapters</a>.
    The outline has been adapted for the IDS, with the numbering system generally maintained;
    and this remains the same for all the wordlists. Buck's dictionary contains approximately
    1200 potential entries (not complete for all languages, of course). The IDS adaptation
    contains
        <a href="${request.route_url('parameters')}">${entries} entries</a>.
    If a form does not exist in a certain area of the world, the entry
    is left blank. The entries are given with English as the first heading, and where
    appropriate the language(s) of the area alongside, for example, English, Portuguese, and
    Spanish for indigenous languages of South America.
</%util:section>

<%util:section title="Authors" id="Authors" level="4">
    Each wordlist is the responsibility of an individual
    <a href="${request.route_url('contributors')}">author or team of authors</a>.
    The actual
    contributors of language data, the consultants, generally have a high level of fieldwork
    experience in the language, and are often native speakers of the languages recorded. Much
    of the data being entered into the dictionary is from unpublished field notes, which
    thereby become more widely accessible. In addition, groups of wordlists from a particular
    language family or geographical area have sometimes been produced under the guidance of a
    single author or team of authors. The general editor has overall responsibility for the
    project.
</%util:section>

<%util:section title="Choice of Languages" id="Languages" level="4">
    Ideally, the coverage would be comprehensive, but practical consideration has had to be
    given to:
        <ul>
            <li>availability of publications and fieldwork;</li>
            <li>comparative work done;</li>
            <li>coordination with other research;</li>
            <li>contacts and cooperation of personnel and their expertise.</li>
        </ul>
    Each language that has been entered has been corrected and supported by linguistic experts,
    who were consulted regularly.
</%util:section>

<%util:section title="Compiling the lists" id="Compiling" level="4">
    The production of each wordlist involves sufficient interaction between the general editor,
    the author, and the consultants to assure accuracy. During the initial stages of compilation,
    the general editor acquaints the author and, through the author, the collaborators with the
    outline and organization of the dictionary as a series. The IDS WordList is distributed to
    each author and consultant. As the author and consultants fill in the wordlist, correspondence
    with the general editor deals with such matters as morpheme division, dialect usage,
    orthography, and difficulties in finding the correct translations. The final stage of this
    collaboration results in a pre-publication copy which is sent to the author (and, where
    appropriate, consultants) for final checking.
</%util:section>

<%util:section title="Digital implementation" id="Digital" level="4">
    Advances over the last decades have vastly improved the possibilities for hosting IDS
    material on the internet, well beyond the project's initial expectations. These advances
    have also brought with them challenges in adapting earlier IDS materials and assuring
    consistency and sustainability, considerably delaying the public launch of the new web site.
    Particular thanks go to Hans-Jörg Bibiko and Robert Forkel for meeting these challenges.
    The IDS data are now stored in a machine-readable format that can be posted on the internet.
    This opens unlimited access to IDS data for scholars from all over the world, to use the
    dictionaries for further research.
</%util:section>

<%util:section title="Origin and History of IDS" id="History" level="4">
    The idea for a work such as the IDS came to Mary Ritchie Key while on a Fulbright in Chile
    in 1975 studying the semantic grouping in the cognate sets of comparative studies. This was
    followed by pilot projects at the University of California, Irvine, using comparative data
    of recognized language families. In 1982, a computer science and math major constructed a
    program called ASYNCOG, using three words from C.D. Buck: 'water', 'skin', 'eat'. Scholars
    were contacted who were chosen for their interests in cross-cultural research and for their
    skills and willingness to give time and thought to the objectives of the dictionary series.
    In 1984, an award from the University of California, Irvine Faculty Research Committee to
    launch the Intercontinental Dictionary Series set the series on its way. In 1990, the IDS
    won an Honorable Mention from the Rolex Awards for Enterprise
    In 1998, Bernard Comrie took over from Mary Ritchie Key and continued to develop IDS
    at the Max Planck Institute for Evolutionary Anthropology in Leipzig.
</%util:section>

<%util:section title="Further Possibilities" id="Possibilities" level="4">
    The obvious and immediate product of this intercontinental enterprise is a dictionary series.
    There are other imaginable goals for the future. An IDS center would serve as a clearinghouse
    for comparative work between the continents. It could also serve as a repository for scholars
    to leave their unpublished materials in a place where they would be appreciated and utilized
    in further research. Thus, it would assure preservation and continuity of unpublished
    work-in-progress. And finally, it would bring together data on the languages of the world, in
    such away that would give importance to all languages. This speaks to the unity of all the
    peoples on earth.
</%util:section>

<%util:section title="Acknowledgments" id="Acknowledgments" level="4">
    Bernard Comrie (University of California, Santa Barbara) wishes to acknowledge the
    support of the Max Planck Society (especially
    through the Max Planck Institute for Evolutionary Anthropology) in updating and expanding
    the IDS, and of Mary Ritchie Key for a generous grant that enabled the collection of IDS
    lists for Tai-Kadai and Mon-Khmer languages of Southeast Asia.
</%util:section>

<%util:section title="Reference" id="Reference" level="4">
    <blockquote>
    Borin, Lars & Comrie, Bernard & Saxena, Anju. 2013.
    The Intercontinental Dictionary Series: A rich and principled database for language comparison.
    In Borin, Lars & Saxena, Anju (eds.). Approaches to measuring linguistic differences, 285-302.
    (Trends in Linguistics, 265.) Berlin: De Gruyter Mouton.
    </blockquote>
</%util:section>
