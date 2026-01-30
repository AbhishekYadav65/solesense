const state = {
  simulationResult: null
};

const runButton = document.getElementById("runSim");
const overviewEl = document.getElementById("overviewContent");

runButton.addEventListener("click", async () => {
  overviewEl.textContent = "Running simulation…";

  const payload = {
    body_weight: Number(document.getElementById("bodyWeight").value),
    foot_size: Number(document.getElementById("footSize").value),
    arch_type: document.getElementById("archType").value,
    activity_mode: document.getElementById("activityMode").value,
    sole_stiffness: Number(document.getElementById("soleStiffness").value),
    material_durability: Number(document.getElementById("materialDurability").value),
    steps: 50
  };

  try {
    const res = await fetch("http://127.0.0.1:5000/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    state.simulationResult = data;

    renderOverview(data);

  } catch (err) {
    overviewEl.textContent = "Simulation failed.";
    console.error(err);
  }
});

function renderOverview(data) {
  const o = data.overview;

  overviewEl.innerHTML = `
    <strong>Scenario:</strong> ${o.scenario_type}<br/>
    <strong>Stability:</strong> ${o.stability}<br/>
    <strong>Alignment:</strong> ${o.alignment_regime}<br/>
    <strong>Comfort Change:</strong> ${o.comfort_change}
  `;
}
