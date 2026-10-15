/* Open Parafrase Weergave — ontwerplaag van de lezer.
 *
 * Kleine, losse gedragingen bovenop de bestaande lezer, zonder de logica
 * ervan te veranderen:
 *   - startscherm (index.html zonder #boek/hoofdstuk);
 *   - gouden voortgangslijn onder de bovenbalk;
 *   - "Lees verder" onderaan elk hoofdstuk, met de titel van het volgende;
 *   - duimbalk op mobiel (Aa-knop, wegschuiven tijdens het lezen);
 *   - instellingenpaneel: voorbeeldtekst bovenaan en regelafstand als
 *     drie knoppen in plaats van een schuifje.
 */
(function () {
    'use strict';

    var root = document.documentElement;

    /* ---------- Startscherm ---------- */
    function toonStart() {
        if (!root.classList.contains('opv-startscherm')) return;
        window.scrollTo(0, 0);
    }
    document.addEventListener('opv:startscherm', toonStart);

    function reactie(knop) {
        if (window.Feedback && typeof window.Feedback.open === 'function') {
            window.Feedback.open({ ref: 'Open Parafrase Weergave (algemeen)', text: '' });
        } else {
            location.href = 'over-opv.html#status';
        }
        if (knop) knop.blur();
    }

    /* ---------- Voortgangslijn ---------- */
    var lijn = null;
    var gepland = false;
    function werkVoortgangBij() {
        gepland = false;
        if (!lijn) lijn = document.querySelector('#opv-voortgang i');
        var houder = document.getElementById('verses-container');
        if (!lijn || !houder) return;
        var rect = houder.getBoundingClientRect();
        var hoogte = rect.height || 1;
        var deel = (window.innerHeight * 0.5 - rect.top) / hoogte;
        deel = Math.max(0, Math.min(1, deel));
        lijn.style.transform = 'scaleX(' + deel.toFixed(4) + ')';
    }
    function planVoortgang() {
        if (gepland) return;
        gepland = true;
        requestAnimationFrame(werkVoortgangBij);
    }

    /* ---------- Duimbalk: wegschuiven bij naar beneden lezen ---------- */
    var vorigeY = window.scrollY;
    function duimbalkBijScroll() {
        var y = window.scrollY;
        var dy = y - vorigeY;
        if (Math.abs(dy) < 6) return;
        var onderaan = window.innerHeight + y >= document.documentElement.scrollHeight - 24;
        var weg = dy > 0 && y > 120 && !onderaan;
        document.body.classList.toggle('opv-duim-weg', weg);
        vorigeY = y;
    }

    window.addEventListener('scroll', function () {
        planVoortgang();
        duimbalkBijScroll();
    }, { passive: true });
    window.addEventListener('resize', planVoortgang);

    /* ---------- Lees verder ---------- */
    function esc(tekst) {
        return String(tekst == null ? '' : tekst).replace(/[&<>"]/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
        });
    }

    async function buren(bookId, chapter) {
        var manifest = await DataLoader.loadManifest();
        var mode = (window.Opties && Opties.state && Opties.state.boekvolgorde) || 'canoniek';
        var volgorde = (typeof getFlatBookOrder === 'function')
            ? getFlatBookOrder(mode, manifest)
            : manifest.books.map(function (b) { return b.id; });
        var perId = {};
        manifest.books.forEach(function (b) { perId[b.id] = b; });
        var boek = perId[bookId];
        if (!boek) return {};
        var hfst = boek.chaptersIncluded || [];
        var i = hfst.indexOf(chapter);
        var b = volgorde.indexOf(bookId);
        var vorige = null, volgende = null;
        if (i > 0) vorige = { boek: boek, ch: hfst[i - 1] };
        else if (b > 0 && perId[volgorde[b - 1]]) {
            var vb = perId[volgorde[b - 1]];
            vorige = { boek: vb, ch: vb.chaptersIncluded[vb.chaptersIncluded.length - 1] };
        }
        if (i >= 0 && i < hfst.length - 1) volgende = { boek: boek, ch: hfst[i + 1] };
        else if (b >= 0 && b < volgorde.length - 1 && perId[volgorde[b + 1]]) {
            var nb = perId[volgorde[b + 1]];
            volgende = { boek: nb, ch: nb.chaptersIncluded[0] };
        }
        return { vorige: vorige, volgende: volgende };
    }

    var verderGeneratie = 0;
    async function vulVerder(bookId, chapter) {
        var nav = document.getElementById('opv-verder');
        if (!nav || typeof DataLoader === 'undefined') return;
        var generatie = ++verderGeneratie;
        try {
            var b = await buren(bookId, chapter);
            var titel = '';
            if (b.volgende && window.TekstEditie) {
                try {
                    var data = await TekstEditie.loadChapter(b.volgende.boek.id, b.volgende.ch);
                    titel = (data && data.heading) || '';
                    if (titel && window.Opties && Opties.transformOPV) {
                        var tmp = document.createElement('div');
                        tmp.innerHTML = Opties.transformOPV(esc(titel));
                        titel = tmp.textContent;
                    }
                } catch (e) { titel = ''; }
            }
            if (generatie !== verderGeneratie) return;
            var html = '';
            if (b.vorige) {
                html += '<a class="opv-verder-terug" href="' + Navigation.chapterUrl(b.vorige.boek.id, b.vorige.ch) + '">' +
                    '<span><span aria-hidden="true">← </span>Vorige</span><b>' + esc(b.vorige.boek.nameDutch + ' ' + b.vorige.ch) + '</b></a>';
            }
            if (b.volgende) {
                var naam = b.volgende.boek.nameDutch + ' ' + b.volgende.ch;
                html += '<a class="opv-verder-vol" href="' + Navigation.chapterUrl(b.volgende.boek.id, b.volgende.ch) + '">' +
                    '<span>Lees verder<span aria-hidden="true"> →</span></span><b>' + esc(naam) +
                    (titel ? '<span class="opv-verder-titel"> · ' + esc(titel) + '</span>' : '') + '</b></a>';
            }
            nav.innerHTML = html;
            nav.hidden = !html;
        } catch (e) {
            nav.hidden = true;
        }
    }

    document.addEventListener('opv:hoofdstuk-getoond', function (e) {
        var d = e.detail || {};
        if (!d.append && !d.prepend) vulVerder(d.bookId, d.chapter);
        planVoortgang();
    });

    /* ---------- Instellingenpaneel ---------- */
    var SPATIE = [['0', 'Smal'], ['1', 'Normaal'], ['2', 'Ruim']];

    function segmentVoor(range) {
        if (range.dataset.opvSegment) return;
        range.dataset.opvSegment = 'ja';
        var seg = document.createElement('span');
        seg.className = 'opv-seg';
        seg.setAttribute('role', 'group');
        seg.setAttribute('aria-label', 'Regelafstand');
        SPATIE.forEach(function (paar) {
            var knop = document.createElement('button');
            knop.type = 'button';
            knop.textContent = paar[1];
            knop.dataset.waarde = paar[0];
            knop.addEventListener('click', function (ev) {
                ev.preventDefault();
                range.value = paar[0];
                range.dispatchEvent(new Event('input', { bubbles: true }));
                range.dispatchEvent(new Event('change', { bubbles: true }));
                syncSegmenten();
            });
            seg.appendChild(knop);
        });
        range.classList.add('opv-verborgen-range');
        range.setAttribute('tabindex', '-1');
        range.setAttribute('aria-hidden', 'true');
        range.insertAdjacentElement('afterend', seg);
        var rij = range.closest('label');
        if (rij) rij.classList.add('opv-rij-seg');
    }

    function syncSegmenten() {
        document.querySelectorAll('#sidebar-right .opv-seg').forEach(function (seg) {
            var range = seg.previousElementSibling;
            if (!range) return;
            seg.querySelectorAll('button').forEach(function (knop) {
                knop.setAttribute('aria-pressed', knop.dataset.waarde === String(range.value) ? 'true' : 'false');
            });
        });
    }

    function werkVoorbeeldBij() {
        var gn = document.querySelector('#sidebar-right .opv-voorbeeld [data-gn]');
        if (!gn) return;
        var basis = 'De HEERE is mijn Herder';
        gn.innerHTML = (window.Opties && Opties.transformOPV) ? Opties.transformOPV(basis) : basis;
    }

    function verrijkPaneel() {
        var dialoog = document.getElementById('sidebar-right');
        if (!dialoog || dialoog.dataset.opvVerrijkt) return;
        var body = document.getElementById('sidebar-right-body');
        if (!body || body.dataset.categoriesBuilt !== 'true') return;
        dialoog.dataset.opvVerrijkt = 'ja';

        var vb = document.createElement('div');
        vb.className = 'opv-voorbeeld';
        vb.setAttribute('aria-hidden', 'true');
        vb.innerHTML =
            '<p><span data-gn>De HEERE is mijn Herder</span>; mij ontbreekt niets.</p>' +
            '<p>Hij zei tegen hen: <span class="god-speaks"><i>Kom maar kijken.</i></span> Ze gingen mee en zagen waar Hij verbleef.</p>';
        body.insertBefore(vb, body.firstChild);

        dialoog.querySelectorAll('input[type="range"]').forEach(segmentVoor);

        var kleiner = document.getElementById('options-zoom-out');
        var groter = document.getElementById('options-zoom-in');
        if (kleiner) { kleiner.textContent = 'A'; kleiner.classList.add('opv-a-klein'); }
        if (groter) { groter.textContent = 'A'; groter.classList.add('opv-a-groot'); }

        dialoog.addEventListener('change', function () {
            syncSegmenten();
            werkVoorbeeldBij();
        });
        syncSegmenten();
        werkVoorbeeldBij();
    }

    /* ---------- Opstarten ---------- */
    function init() {
        document.querySelectorAll('[data-opv-reactie]').forEach(function (knop) {
            knop.addEventListener('click', function () { reactie(knop); });
        });
        var aa = document.getElementById('opv-duim-aa');
        if (aa) {
            aa.addEventListener('click', function () {
                if (window.OptionsPanel) window.OptionsPanel.open(aa);
            });
        }
        // Na het openen synchroniseert het paneel zijn spiegels; daarna de
        // regelafstandknoppen en het voorbeeld bijwerken.
        document.querySelectorAll('#topnav-weergave, #opv-duim-aa').forEach(function (knop) {
            knop.addEventListener('click', function () {
                setTimeout(function () { verrijkPaneel(); syncSegmenten(); werkVoorbeeldBij(); }, 0);
            });
        });
        verrijkPaneel();
        toonStart();
        planVoortgang();
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
