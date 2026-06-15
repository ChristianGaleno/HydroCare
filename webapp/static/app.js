// ============================================================
//  HydroCare frontend logic
// ============================================================
const $ = (sel) => document.querySelector(sel);

const els = {
  dropzone: $("#dropzone"),
  fileInput: $("#fileInput"),
  cameraInput: $("#cameraInput"),
  uploadBtn: $("#uploadBtn"),
  cameraBtn: $("#cameraBtn"),
  dropEmpty: $("#dropEmpty"),
  dropPreview: $("#dropPreview"),
  previewImg: $("#previewImg"),
  resetBtn: $("#resetBtn"),
  analyzeBtn: $("#analyzeBtn"),
  errorMsg: $("#errorMsg"),
  // result
  resultSection: $("#resultSection"),
  resultImg: $("#resultImg"),
  resultKind: $("#resultKind"),
  resultCrop: $("#resultCrop"),
  resultCondition: $("#resultCondition"),
  resultSummary: $("#resultSummary"),
  ringFg: $("#ringFg"),
  confValue: $("#confValue"),
  tipsList: $("#tipsList"),
  altList: $("#altList"),
  againBtn: $("#againBtn"),
  // misc
  statusDot: $("#statusDot"),
  statusText: $("#statusText"),
  cropGrid: $("#cropGrid"),
};

let selectedFile = null;
const RING_CIRCUMFERENCE = 2 * Math.PI * 52; // r=52 -> ~326.7

// ---------- helpers ----------
function showError(msg) {
  els.errorMsg.textContent = msg;
  els.errorMsg.hidden = false;
}
function clearError() { els.errorMsg.hidden = true; }

function setFile(file) {
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    showError("Please choose an image file (JPG or PNG).");
    return;
  }
  clearError();
  selectedFile = file;
  const url = URL.createObjectURL(file);
  els.previewImg.src = url;
  els.dropEmpty.hidden = true;
  els.dropPreview.hidden = false;
  els.analyzeBtn.disabled = false;
}

function resetScanner() {
  selectedFile = null;
  els.fileInput.value = "";
  els.cameraInput.value = "";
  els.dropEmpty.hidden = false;
  els.dropPreview.hidden = true;
  els.previewImg.src = "";
  els.analyzeBtn.disabled = true;
  clearError();
}

// ---------- input wiring ----------
els.uploadBtn.addEventListener("click", (e) => { e.stopPropagation(); els.fileInput.click(); });
els.cameraBtn.addEventListener("click", (e) => { e.stopPropagation(); els.cameraInput.click(); });
els.dropzone.addEventListener("click", () => { if (els.dropPreview.hidden) els.fileInput.click(); });
els.dropzone.addEventListener("keydown", (e) => {
  if ((e.key === "Enter" || e.key === " ") && els.dropPreview.hidden) { e.preventDefault(); els.fileInput.click(); }
});

els.fileInput.addEventListener("change", (e) => setFile(e.target.files[0]));
els.cameraInput.addEventListener("change", (e) => setFile(e.target.files[0]));
els.resetBtn.addEventListener("click", (e) => { e.stopPropagation(); resetScanner(); });

["dragenter", "dragover"].forEach((ev) =>
  els.dropzone.addEventListener(ev, (e) => { e.preventDefault(); els.dropzone.classList.add("dragover"); })
);
["dragleave", "drop"].forEach((ev) =>
  els.dropzone.addEventListener(ev, (e) => { e.preventDefault(); els.dropzone.classList.remove("dragover"); })
);
els.dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files && e.dataTransfer.files[0];
  if (file) setFile(file);
});

// ---------- analyze ----------
els.analyzeBtn.addEventListener("click", analyze);
els.againBtn.addEventListener("click", () => {
  resetScanner();
  els.resultSection.hidden = true;
  document.getElementById("scanner").scrollIntoView({ behavior: "smooth", block: "center" });
});

async function analyze() {
  if (!selectedFile) return;
  clearError();
  setBusy(true);

  const form = new FormData();
  form.append("file", selectedFile);

  try {
    const res = await fetch("/api/predict", { method: "POST", body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error (${res.status})`);
    }
    const data = await res.json();
    renderResult(data);
  } catch (err) {
    showError(err.message || "Something went wrong analyzing the image.");
  } finally {
    setBusy(false);
  }
}

function setBusy(busy) {
  els.dropzone.classList.toggle("scanning", busy);
  els.analyzeBtn.disabled = busy || !selectedFile;
  els.analyzeBtn.querySelector(".btn-label").textContent = busy ? "Analyzing…" : "Analyze leaf";
  els.analyzeBtn.querySelector(".spinner").hidden = !busy;
}

// ---------- render ----------
function renderResult(data) {
  const best = data.best;
  els.resultImg.src = els.previewImg.src;

  els.resultKind.textContent = best.kind === "healthy" ? "Healthy" : best.kind === "pest" ? "Pest" : "Disease";
  els.resultKind.className = "result-kind " + best.kind;

  els.resultCrop.textContent = best.crop;
  els.resultCondition.textContent = best.condition;
  els.resultSummary.textContent = best.summary;

  // confidence ring + color
  const conf = best.confidence;
  els.confValue.textContent = `${Math.round(conf)}%`;
  const ringColor = conf >= 75 ? "var(--green-500)" : conf >= 50 ? "var(--leaf-amber)" : "var(--danger)";
  els.ringFg.style.stroke = ringColor;
  els.ringFg.style.strokeDasharray = RING_CIRCUMFERENCE;
  els.ringFg.style.strokeDashoffset = RING_CIRCUMFERENCE; // reset for animation
  requestAnimationFrame(() => {
    els.ringFg.style.strokeDashoffset = RING_CIRCUMFERENCE * (1 - conf / 100);
  });

  // tips
  els.tipsList.innerHTML = "";
  best.tips.forEach((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    els.tipsList.appendChild(li);
  });

  // alternatives
  els.altList.innerHTML = "";
  data.predictions.forEach((p, i) => {
    const row = document.createElement("li");
    row.className = "alt-row";
    row.innerHTML = `
      <div class="alt-top">
        <span class="alt-name">${escapeHtml(p.display)}</span>
        <span class="alt-pct">${p.confidence.toFixed(1)}%</span>
      </div>
      <div class="alt-bar"><div class="alt-fill"></div></div>`;
    els.altList.appendChild(row);
    const fill = row.querySelector(".alt-fill");
    setTimeout(() => { fill.style.width = `${p.confidence}%`; }, 80 + i * 120);
  });

  els.resultSection.hidden = false;
  els.resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// ---------- health + crops ----------
async function loadHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    els.statusDot.classList.add("online");
    els.statusText.textContent = `model ready · ${data.device.toUpperCase()}`;
  } catch {
    els.statusDot.classList.add("offline");
    els.statusText.textContent = "model offline";
  }
}

async function loadCrops() {
  try {
    const res = await fetch("/api/crops");
    const data = await res.json();
    // update hero stats
    setText("#statClasses", data.total_classes);
    setText("#statClassesBig", data.total_classes);
    setText("#statCrops", data.count);
    setText("#statCropsBig", data.count);

    els.cropGrid.innerHTML = "";
    data.crops.forEach((c) => {
      const details = document.createElement("details");
      details.className = "crop-card";
      const chips = c.conditions.map((cond) => {
        const healthy = cond.toLowerCase() === "healthy";
        return `<span class="cond-chip ${healthy ? "healthy" : ""}">${escapeHtml(cond)}</span>`;
      }).join("");
      details.innerHTML = `
        <summary>
          <span>${escapeHtml(c.crop)}</span>
          <span class="crop-count">${c.conditions.length}</span>
        </summary>
        <div class="crop-conds">${chips}</div>`;
      els.cropGrid.appendChild(details);
    });
  } catch {
    els.cropGrid.innerHTML = `<div class="crop-loading">Couldn't load crop list.</div>`;
  }
}

function setText(sel, val) { const el = $(sel); if (el) el.textContent = val; }

// ---------- init ----------
loadHealth();
loadCrops();
