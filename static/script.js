(function () {
  const N = parseInt(document.getElementById("grid").getAttribute("data-n"), 10);
  const MAX_OBS = parseInt(document.getElementById("grid").getAttribute("data-max-obs"), 10);

  let startCell = null;
  let endCell = null;
  const obstacles = [];

  const startBadge = document.getElementById("badge-start");
  const endBadge = document.getElementById("badge-end");
  const obsBadge = document.getElementById("badge-obs");
  const btnEvaluate = document.getElementById("btn-evaluate");
  const btnOptimize = document.getElementById("btn-optimize");
  const rlResults = document.getElementById("rl-results");

  // ── Helpers ────────────────────────────────────────────────────────────────
  function updateBadges() {
    startBadge.textContent = startCell ? "Start: set ✓" : "Start: not set";
    endBadge.textContent = endCell ? "End: set ✓" : "End: not set";
    obsBadge.textContent = `Obstacles: ${obstacles.length} / ${MAX_OBS}`;
    // Enable evaluate and optimize buttons only when both start and end are set
    const enableButtons = (startCell && endCell);
    btnEvaluate.disabled = !enableButtons;
    btnOptimize.disabled = !enableButtons;
  }

  function clearCell(cell) {
    cell.classList.remove("start", "end", "obstacle");
    if (cell === startCell) startCell = null;
    if (cell === endCell) endCell = null;
    const obsIdx = obstacles.indexOf(cell);
    if (obsIdx > -1) obstacles.splice(obsIdx, 1);
  }

  function cellRC(cell) {
    return [
      parseInt(cell.getAttribute("data-row"), 10),
      parseInt(cell.getAttribute("data-col"), 10)
    ];
  }

  // ── Click Handler ──────────────────────────────────────────────────────────
  function onCellClick(e) {
    const cell = e.currentTarget;

    if (cell.classList.contains("start") ||
      cell.classList.contains("end") ||
      cell.classList.contains("obstacle")) {
      clearCell(cell);
      updateBadges();
      return;
    }

    if (!startCell) {
      startCell = cell;
      cell.classList.add("start");
    } else if (!endCell) {
      endCell = cell;
      cell.classList.add("end");
    } else if (obstacles.length < MAX_OBS) {
      obstacles.push(cell);
      cell.classList.add("obstacle");
    }

    updateBadges();
  }

  // ── Policy Evaluation & Optimization ───────────────────────────────────────
  function buildResultGrid(containerId, cellFn) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    const table = document.createElement("table");
    table.className = "result-grid";

    for (let r = 0; r < N; r++) {
      const tr = document.createElement("tr");
      for (let c = 0; c < N; c++) {
        const td = document.createElement("td");
        cellFn(td, r, c);
        tr.appendChild(td);
      }
      table.appendChild(tr);
    }
    container.appendChild(table);
  }

  function getCellClass(r, c, startRC, endRC, obsSet) {
    const key = `${r},${c}`;
    if (key === `${startRC[0]},${startRC[1]}`) return "r-start";
    if (key === `${endRC[0]},${endRC[1]}`) return "r-end";
    if (obsSet.has(key)) return "r-obstacle";
    return "";
  }

  function getValueClass(v) {
    if (v > 0) return "val-pos";
    if (v < 0) return "val-neg";
    return "val-zero";
  }

  // --- Evaluate Random Policy ---
  btnEvaluate.addEventListener("click", function () {
    runRLProcess("/evaluate", "🧠 Evaluating…", false);
  });

  // --- Find Optimal Path ---
  btnOptimize.addEventListener("click", function () {
    runRLProcess("/optimize", "🌟 Optimizing…", true);
  });

  function runRLProcess(endpoint, loadingText, isOptimal) {
    if (!startCell || !endCell) return;

    const startRC = cellRC(startCell);
    const endRC = cellRC(endCell);
    const obsArr = obstacles.map(cellRC);
    const obsSet = new Set(obsArr.map(([r, c]) => `${r},${c}`));

    // Show loading state
    btnEvaluate.disabled = true;
    btnOptimize.disabled = true;
    if (isOptimal) {
      btnOptimize.innerHTML = `<span class="spinner"></span> ${loadingText}`;
    } else {
      btnEvaluate.innerHTML = `<span class="spinner"></span> ${loadingText}`;
    }

    rlResults.style.display = "none";

    // Clear previous path highlights in the main grid
    document.querySelectorAll(".path-highlight").forEach(el => el.classList.remove("path-highlight"));

    fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ n: N, start: startRC, end: endRC, obstacles: obsArr }),
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        const { arrows, values, path } = data;

        // Update titles based on mode
        const policyTitle = document.querySelector(".policy-title");
        const valueTitle = document.querySelector(".value-title");
        if (isOptimal) {
          policyTitle.innerHTML = "🌟 Optimal Policy π*";
          valueTitle.innerHTML = "📈 Optimal Value V*";
        } else {
          policyTitle.innerHTML = "🗺 Policy Matrix (Random)";
          valueTitle.innerHTML = "📈 Value Matrix V(s)";
        }

        // ── Policy Matrix ──
        buildResultGrid("policy-grid-container", function (td, r, c) {
          const cls = getCellClass(r, c, startRC, endRC, obsSet);
          if (cls) { td.className = cls; return; }

          const arrowList = arrows[`${r},${c}`];   // array e.g. ["↑","→"]
          if (arrowList && arrowList.length) {
            const wrap = document.createElement("div");
            wrap.className = "arrow-wrap";
            arrowList.forEach(function (sym) {
              const span = document.createElement("span");
              span.className = "cell-arrow";
              span.textContent = sym;
              wrap.appendChild(span);
            });
            td.appendChild(wrap);
          }
        });

        // ── Value Matrix ──
        buildResultGrid("value-grid-container", function (td, r, c) {
          const cls = getCellClass(r, c, startRC, endRC, obsSet);
          if (cls) {
            td.className = cls;
            if (cls === "r-end") {
              const span = document.createElement("span");
              span.className = "cell-value val-zero";
              span.textContent = "0";
              td.appendChild(span);
            }
            return;
          }

          const v = values[`${r},${c}`];
          if (v !== undefined) {
            const span = document.createElement("span");
            span.className = "cell-value " + getValueClass(v);
            span.textContent = v.toFixed(2);
            td.appendChild(span);
          }
        });

        // ── Draw Path if provided ──
        if (path && path.length > 0) {
          // Add highlights to the main grid
          const mainGridCells = document.querySelectorAll("#grid td");
          const pathSet = new Set(path.map(([r, c]) => `${r},${c}`));

          mainGridCells.forEach(td => {
            const r = parseInt(td.getAttribute("data-row"), 10);
            const c = parseInt(td.getAttribute("data-col"), 10);
            if (pathSet.has(`${r},${c}`)) {
              td.classList.add("path-highlight");
            }
          });

          // Add highlights to result grids
          const policyGridCells = document.querySelectorAll("#policy-grid-container td");
          const valueGridCells = document.querySelectorAll("#value-grid-container td");

          let idx = 0;
          for (let r = 0; r < N; r++) {
            for (let c = 0; c < N; c++) {
              if (pathSet.has(`${r},${c}`)) {
                if (policyGridCells[idx]) policyGridCells[idx].classList.add("path-highlight");
                if (valueGridCells[idx]) valueGridCells[idx].classList.add("path-highlight");
              }
              idx++;
            }
          }
        }

        rlResults.style.display = "block";
      })
      .catch(function (err) {
        console.error("RL error:", err);
        alert("Evaluation failed. See console.");
      })
      .finally(function () {
        btnEvaluate.disabled = false;
        btnOptimize.disabled = false;
        btnEvaluate.innerHTML = "🧠 Evaluate Policy (Random)";
        btnOptimize.innerHTML = "🌟 Find Optimal Path (V*)";
      });
  }

  // ── Init ──────────────────────────────────────────────────────────────────
  document.querySelectorAll("#grid td").forEach(function (td) {
    td.addEventListener("click", onCellClick);
  });

  updateBadges();
}());
