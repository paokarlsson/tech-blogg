/* Poddspelare — progressiv förbättring av <audio controls>.
 *
 * Markupen levereras med webbläsarens egna reglage påslagna. Det här skriptet
 * stänger av dem och visar det egna gränssnittet i stället, så att en läsare
 * utan JavaScript ändå kan lyssna.
 *
 * Reglagen är <button> och <input type="range">, så tangentbord och
 * skärmläsare fungerar av sig själva — skriptet håller bara etiketter och
 * ifyllnad i synk. */
(function () {
  "use strict";

  var tid = function (s) {
    if (!isFinite(s)) return "--:--";
    var m = Math.floor(s / 60);
    var r = Math.floor(s % 60);
    return m + ":" + (r < 10 ? "0" : "") + r;
  };

  // Ifyllnaden av ett range-reglage kan inte göras i ren CSS — andelen skickas
  // in som en custom property som gradienten i style.css läser.
  var fyll = function (el) {
    var min = Number(el.min || 0);
    var max = Number(el.max || 100);
    var andel = max > min ? ((Number(el.value) - min) / (max - min)) * 100 : 0;
    el.style.setProperty("--progress", andel + "%");
  };

  var HASTIGHETER = [1, 1.25, 1.5, 1.75, 2];

  document.querySelectorAll("[data-podplayer]").forEach(function (rot) {
    var ljud = rot.querySelector(".podplayer-audio");
    var ui = rot.querySelector(".podplayer-ui");
    if (!ljud || !ui) return;

    var toggle = rot.querySelector(".podplayer-toggle");
    var seek = rot.querySelector(".podplayer-seek");
    var nu = rot.querySelector(".podplayer-now");
    var langd = rot.querySelector(".podplayer-dur");
    var rate = rot.querySelector(".podplayer-rate");
    var mute = rot.querySelector(".podplayer-mute");
    var volym = rot.querySelector(".podplayer-volume");
    var ikonSpela = rot.querySelector(".i-play");
    var ikonPaus = rot.querySelector(".i-pause");
    var ikonVol = rot.querySelector(".i-vol");
    var ikonTyst = rot.querySelector(".i-muted");

    // Byt ut webbläsarens spelare mot vår egen.
    ljud.removeAttribute("controls");
    ljud.classList.add("podplayer-audio--dold");
    ui.hidden = false;

    var drar = false;

    toggle.addEventListener("click", function () {
      if (ljud.paused) ljud.play();
      else ljud.pause();
    });

    var visaLage = function () {
      var spelar = !ljud.paused;
      ikonSpela.hidden = spelar;
      ikonPaus.hidden = !spelar;
      toggle.setAttribute("aria-label", spelar ? "Pausa avsnittet" : "Spela avsnittet");
      rot.classList.toggle("spelar", spelar);
    };
    ljud.addEventListener("play", visaLage);
    ljud.addEventListener("pause", visaLage);
    ljud.addEventListener("ended", visaLage);

    ljud.addEventListener("loadedmetadata", function () {
      langd.textContent = tid(ljud.duration);
    });
    if (ljud.readyState > 0) langd.textContent = tid(ljud.duration);

    ljud.addEventListener("timeupdate", function () {
      nu.textContent = tid(ljud.currentTime);
      if (drar || !isFinite(ljud.duration)) return;
      seek.value = String((ljud.currentTime / ljud.duration) * 1000);
      fyll(seek);
    });

    // pointerdown/up i stället för bara "change": annars hoppar reglaget
    // tillbaka under tiden man drar, eftersom timeupdate skriver över värdet.
    seek.addEventListener("pointerdown", function () { drar = true; });
    seek.addEventListener("input", function () {
      fyll(seek);
      if (isFinite(ljud.duration)) nu.textContent = tid((seek.value / 1000) * ljud.duration);
    });
    var slappSeek = function () {
      if (!drar && document.activeElement !== seek) return;
      drar = false;
      if (isFinite(ljud.duration)) ljud.currentTime = (seek.value / 1000) * ljud.duration;
    };
    seek.addEventListener("pointerup", slappSeek);
    seek.addEventListener("change", slappSeek);

    rate.addEventListener("click", function () {
      var i = (HASTIGHETER.indexOf(ljud.playbackRate) + 1) % HASTIGHETER.length;
      ljud.playbackRate = HASTIGHETER[i];
      rate.textContent = String(HASTIGHETER[i]).replace(".", ",") + "×";
    });

    volym.addEventListener("input", function () {
      ljud.volume = Number(volym.value);
      ljud.muted = ljud.volume === 0;
      fyll(volym);
      visaVolym();
    });

    var visaVolym = function () {
      var tyst = ljud.muted || ljud.volume === 0;
      ikonVol.hidden = tyst;
      ikonTyst.hidden = !tyst;
      mute.setAttribute("aria-label", tyst ? "Slå på ljudet" : "Stäng av ljudet");
    };

    mute.addEventListener("click", function () {
      ljud.muted = !ljud.muted;
      volym.value = ljud.muted ? "0" : String(ljud.volume || 1);
      if (!ljud.muted && ljud.volume === 0) ljud.volume = 1;
      fyll(volym);
      visaVolym();
    });

    fyll(seek);
    fyll(volym);
    visaLage();
    visaVolym();
  });
})();
