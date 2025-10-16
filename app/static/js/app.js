const manufacturerSelect = document.querySelector("#manufacturer");
const modelSelect = document.querySelector("#model");
const yearSelect = document.querySelector("#year");
const fuelSelect = document.querySelector("#fuel");
const form = document.querySelector("#prediction-form");
const resultCard = document.querySelector("#prediction-result");
const errorCard = document.querySelector("#prediction-error");
const resultValue = document.querySelector("#predicted-price");
const errorMessage = document.querySelector("#error-message");

function resetSelect(selectEl, placeholder) {
  selectEl.innerHTML = "";
  const option = document.createElement("option");
  option.value = "";
  option.textContent = placeholder;
  option.disabled = true;
  option.selected = true;
  selectEl.appendChild(option);
}

function populateSelect(selectEl, values) {
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = String(value).replace(/\\b\\w/g, (char) => char.toUpperCase());
    selectEl.appendChild(option);
  });
}

function handleManufacturerChange() {
  const manufacturer = manufacturerSelect.value;
  resetSelect(modelSelect, manufacturer ? "Choose model…" : "Select manufacturer first");
  resetSelect(yearSelect, "Select model first");
  modelSelect.disabled = true;
  yearSelect.disabled = true;

  if (!manufacturer || !MANUFACTURER_MODELS[manufacturer]) {
    return;
  }

  populateSelect(modelSelect, MANUFACTURER_MODELS[manufacturer]);
  modelSelect.disabled = false;
}

function handleModelChange() {
  const manufacturer = manufacturerSelect.value;
  const model = modelSelect.value;
  resetSelect(yearSelect, model ? "Choose model year…" : "Select model first");
  yearSelect.disabled = true;

  const years = YEAR_OPTIONS[manufacturer]?.[model];
  if (!years || years.length === 0) {
    return;
  }

  populateSelect(yearSelect, years);
  yearSelect.disabled = false;
}

async function submitPrediction(event) {
  event.preventDefault();
  errorCard.classList.add("hidden");
  resultCard.classList.add("hidden");

  if (!manufacturerSelect.value || !modelSelect.value || !yearSelect.value || !fuelSelect.value) {
    errorMessage.textContent = "Please select manufacturer, model, year, and fuel.";
    errorCard.classList.remove("hidden");
    return;
  }

  const payload = {
    manufacturer: manufacturerSelect.value,
    model: modelSelect.value,
    year: parseInt(yearSelect.value, 10),
    fuel: fuelSelect.value,
  };

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Prediction failed.");
    }

    resultValue.textContent = `$${data.predicted_price.toLocaleString()}`;
    resultCard.classList.remove("hidden");
  } catch (error) {
    errorMessage.textContent = error.message;
    errorCard.classList.remove("hidden");
  }
}

manufacturerSelect.addEventListener("change", handleManufacturerChange);
modelSelect.addEventListener("change", handleModelChange);
form.addEventListener("submit", submitPrediction);
