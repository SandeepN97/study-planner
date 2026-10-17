// Progressive enhancement: replaces each <select> with an accessible listbox dropdown.
// The native <select> stays in the DOM (hidden) so form submission is unchanged.
(function () {
  var uid = 0;

  function enhance(select) {
    var id = "dd" + ++uid;
    var wrap = document.createElement("div");
    wrap.className = "dd";

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "dd-btn";
    btn.setAttribute("aria-haspopup", "listbox");
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-controls", id);

    var list = document.createElement("ul");
    list.className = "dd-list";
    list.id = id;
    list.setAttribute("role", "listbox");
    list.tabIndex = -1;
    list.hidden = true;

    var options = Array.prototype.map.call(select.options, function (opt, i) {
      var li = document.createElement("li");
      li.className = "dd-opt";
      li.id = id + "-" + i;
      li.setAttribute("role", "option");
      li.textContent = opt.textContent;
      li.dataset.index = i;
      list.appendChild(li);
      return li;
    });

    var active = select.selectedIndex;

    function sync() {
      var sel = select.selectedIndex;
      btn.textContent = select.options[sel].textContent;
      options.forEach(function (li, i) {
        li.setAttribute("aria-selected", i === sel ? "true" : "false");
      });
    }

    function setActive(i) {
      active = Math.max(0, Math.min(options.length - 1, i));
      options.forEach(function (li, j) { li.classList.toggle("is-active", j === active); });
      list.setAttribute("aria-activedescendant", options[active].id);
      options[active].scrollIntoView({ block: "nearest" });
    }

    function open() {
      list.hidden = false;
      btn.setAttribute("aria-expanded", "true");
      wrap.classList.add("is-open");
      setActive(select.selectedIndex);
      list.focus({ preventScroll: true });
    }

    function close(refocus) {
      list.hidden = true;
      btn.setAttribute("aria-expanded", "false");
      wrap.classList.remove("is-open");
      if (refocus) btn.focus();
    }

    function choose(i) {
      if (select.selectedIndex !== i) {
        select.selectedIndex = i;
        select.dispatchEvent(new Event("change", { bubbles: true }));
      }
      sync();
      close(true);
    }

    btn.addEventListener("click", function () { list.hidden ? open() : close(true); });
    btn.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); open(); }
    });

    list.addEventListener("click", function (e) {
      var li = e.target.closest(".dd-opt");
      if (li) choose(+li.dataset.index);
    });
    list.addEventListener("mousemove", function (e) {
      var li = e.target.closest(".dd-opt");
      if (li) setActive(+li.dataset.index);
    });
    list.addEventListener("keydown", function (e) {
      switch (e.key) {
        case "ArrowDown": e.preventDefault(); setActive(active + 1); break;
        case "ArrowUp":   e.preventDefault(); setActive(active - 1); break;
        case "Home":      e.preventDefault(); setActive(0); break;
        case "End":       e.preventDefault(); setActive(options.length - 1); break;
        case "Enter":
        case " ":         e.preventDefault(); choose(active); break;
        case "Escape":    e.preventDefault(); close(true); break;
        case "Tab":       close(false); break;
        default:
          if (e.key.length === 1) {
            var ch = e.key.toLowerCase();
            for (var k = 1; k <= options.length; k++) {
              var j = (active + k) % options.length;
              if (options[j].textContent.trim().toLowerCase().indexOf(ch) === 0) { setActive(j); break; }
            }
          }
      }
    });

    document.addEventListener("click", function (e) {
      if (!wrap.contains(e.target)) close(false);
    });

    // Clicking the surrounding <label> focuses the native select; hand focus to the button.
    select.addEventListener("focus", function () { btn.focus(); });

    select.parentNode.insertBefore(wrap, select);
    wrap.appendChild(select);
    wrap.appendChild(btn);
    wrap.appendChild(list);
    select.tabIndex = -1;
    select.setAttribute("aria-hidden", "true");
    wrap.classList.add("is-enhanced");
    sync();
  }

  document.querySelectorAll("select").forEach(enhance);
})();
