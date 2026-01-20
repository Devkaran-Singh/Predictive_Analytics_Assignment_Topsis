const file = document.getElementById("dataset");
const weights = document.getElementById("weights");
const impacts = document.getElementById("impacts");
const email = document.getElementById("email");
const button = document.getElementById("button");

button.addEventListener("click", async (e) => {
  e.preventDefault();
  if (
    file.files.length == 0 ||
    weights.value == "" ||
    impacts.value == "" ||
    email.value == ""
  ) {
    alert("Please fill in all the fields!");
    return;
  }
  const formData = new FormData();
  formData.append("dataset", file.files[0]);
  formData.append("weights", weights.value);
  formData.append("impacts", impacts.value);
  formData.append("email", email.value);

  try {
    const response = await fetch("http://127.0.0.1:5000/upload", {
      method: "POST",
      body: formData,
    });

    console.log("HTTP Status:", response.status);

    const text = await response.text();
    console.log("Raw response from server:", text);

    if (response.ok) {
      alert("SUCCESS: Report generated!");
    } else {
      alert("SERVER ERROR:\n" + text);
    }
  } catch (err) {
    alert("FETCH FAILED — see console");
    console.error("Fetch Error:", err);
  }
});