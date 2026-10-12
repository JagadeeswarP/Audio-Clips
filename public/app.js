document.addEventListener("DOMContentLoaded", () => {
    // Elements
    const presetCards = document.querySelectorAll(".preset-card");
    const pitchSlider = document.getElementById("pitch-slider");
    const rateSlider = document.getElementById("rate-slider");
    const commaSlider = document.getElementById("comma-slider");
    const periodSlider = document.getElementById("period-slider");
    const voiceSelect = document.getElementById("voice-select");

    const pitchVal = document.getElementById("pitch-val");
    const rateVal = document.getElementById("rate-val");
    const commaVal = document.getElementById("comma-val");
    const periodVal = document.getElementById("period-val");

    const scriptInput = document.getElementById("script-input");
    const charCount = document.getElementById("char-count");
    const sampleBtns = document.querySelectorAll(".sample-btn");
    const generateBtn = document.getElementById("generate-btn");
    const formatSsmlBtn = document.getElementById("format-ssml-btn");
    const ssmlBox = document.getElementById("ssml-box");
    const ssmlContent = document.getElementById("ssml-content");
    const closeSsml = document.getElementById("close-ssml");

    const audioCard = document.getElementById("audio-card");
    const audioPlayer = document.getElementById("audio-player");
    const downloadBtn = document.getElementById("download-btn");
    const audioMeta = document.getElementById("audio-meta");
    const canvas = document.getElementById("waveform-canvas");
    const ctx = canvas.getContext("2d");

    let currentPreset = "deep_narrator";
    let samplesData = {};
    let presetsData = {};
    let voicesData = {};

    // Fetch initial presets and samples from backend API
    async function loadInitialData() {
        try {
            const [presetsRes, samplesRes, voicesRes] = await Promise.all([
                fetch("/api/presets"),
                fetch("/api/samples"),
                fetch("/api/voices")
            ]);
            
            if (presetsRes.ok) {
                const data = await presetsRes.json();
                presetsData = data.presets;
            }
            if (samplesRes.ok) {
                const data = await samplesRes.json();
                samplesData = data.samples;
                // Auto load psychology sample if input is empty
                if (!scriptInput.value.trim()) {
                    loadSample("psychology");
                }
            }
            if (voicesRes.ok) {
                const data = await voicesRes.json();
                voicesData = data.voices;
                renderVoiceOptions();
            }
        } catch (err) {
            console.error("Error loading server metadata:", err);
        }
    }

    loadInitialData();

    // Preset Selection
    presetCards.forEach(card => {
        card.addEventListener("click", () => {
            presetCards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            
            currentPreset = card.dataset.preset;
            applyPresetValues(currentPreset);
        });
    });

    function applyPresetValues(presetKey) {
        if (!presetsData[presetKey]) return;
        const config = presetsData[presetKey];
        
        // Extract numeric pitch
        const pitchMatch = config.pitch.match(/(-?\d+)/);
        if (pitchMatch) {
            pitchSlider.value = pitchMatch[1];
            pitchVal.textContent = config.pitch;
        }

        // Extract numeric rate
        const rateMatch = config.rate.match(/(-?\d+)/);
        if (rateMatch) {
            rateSlider.value = rateMatch[1];
            rateVal.textContent = config.rate;
        }

        if (config.pause_comma_ms) {
            commaSlider.value = config.pause_comma_ms;
            commaVal.textContent = config.pause_comma_ms + "ms";
        }

        if (config.pause_period_ms) {
            periodSlider.value = config.pause_period_ms;
            periodVal.textContent = config.pause_period_ms + "ms";
        }

        if (config.voice && voiceSelect.querySelector(`option[value="${config.voice}"]`)) {
            voiceSelect.value = config.voice;
        }
    }

    function renderVoiceOptions() {
        if (!Object.keys(voicesData).length) return;

        voiceSelect.innerHTML = "";
        Object.entries(voicesData).forEach(([voiceId, config]) => {
            const option = document.createElement("option");
            option.value = voiceId;
            option.textContent = `${config.name} - US ${config.gender} (${config.locale})`;
            voiceSelect.appendChild(option);
        });

        const presetVoice = presetsData[currentPreset]?.voice;
        if (presetVoice && voiceSelect.querySelector(`option[value="${presetVoice}"]`)) {
            voiceSelect.value = presetVoice;
        }
    }

    // Sliders input listeners
    pitchSlider.addEventListener("input", (e) => {
        const val = parseInt(e.target.value);
        pitchVal.textContent = (val > 0 ? "+" + val : val) + "Hz";
    });

    rateSlider.addEventListener("input", (e) => {
        const val = parseInt(e.target.value);
        rateVal.textContent = (val > 0 ? "+" + val : val) + "%";
    });

    commaSlider.addEventListener("input", (e) => {
        commaVal.textContent = e.target.value + "ms";
    });

    periodSlider.addEventListener("input", (e) => {
        periodVal.textContent = e.target.value + "ms";
    });

    // Character counter
    scriptInput.addEventListener("input", () => {
        charCount.textContent = `${scriptInput.value.length} characters`;
    });

    // Quick Sample buttons
    sampleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const sampleKey = btn.dataset.sample;
            loadSample(sampleKey);
        });
    });

    function loadSample(key) {
        if (samplesData[key]) {
            scriptInput.value = samplesData[key].script;
            charCount.textContent = `${scriptInput.value.length} characters`;
        }
    }

    // View SSML Code
    formatSsmlBtn.addEventListener("click", async () => {
        const text = scriptInput.value.trim();
        if (!text) {
            alert("Please enter a script before viewing SSML code.");
            return;
        }

        try {
            const response = await fetch("/api/ssml-preview", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(getPayload())
            });
            if (response.ok) {
                const data = await response.json();
                ssmlContent.textContent = data.ssml;
                ssmlBox.classList.remove("hidden");
            }
        } catch (err) {
            console.error("SSML preview error:", err);
        }
    });

    closeSsml.addEventListener("click", () => {
        ssmlBox.classList.add("hidden");
    });

    // Helper payload generator
    function getPayload() {
        return {
            text: scriptInput.value,
            preset: currentPreset,
            voice: voiceSelect.value,
            pitch: (parseInt(pitchSlider.value) > 0 ? "+" : "") + pitchSlider.value + "Hz",
            rate: (parseInt(rateSlider.value) > 0 ? "+" : "") + rateSlider.value + "%",
            comma_pause: parseInt(commaSlider.value),
            period_pause: parseInt(periodSlider.value)
        };
    }

    // Generate Audio Speech
    generateBtn.addEventListener("click", async () => {
        const text = scriptInput.value.trim();
        if (!text) {
            alert("Please enter a script text to generate voice narration.");
            return;
        }

        // Loading state
        generateBtn.disabled = true;
        generateBtn.querySelector("span").textContent = "Synthesizing Natural Voice...";

        try {
            const response = await fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(getPayload())
            });

            if (!response.ok) {
                const errData = await response.json();
                alert(`Error: ${errData.detail || "Synthesis failed"}`);
                return;
            }

            const data = await response.json();
            if (data.success) {
                audioPlayer.src = data.audio_url;
                downloadBtn.href = data.audio_url;
                downloadBtn.download = data.filename;
                
                audioMeta.textContent = `${data.voice || voiceSelect.value} • Pitch: ${pitchSlider.value}Hz • Rate: ${rateSlider.value}% • Size: ${(data.file_size / 1024).toFixed(1)} KB`;
                audioCard.classList.remove("hidden");
                
                // Auto play
                audioPlayer.play();
                drawWaveform();
            }
        } catch (err) {
            console.error("Audio generation exception:", err);
            alert("Audio synthesis error occurred.");
        } finally {
            generateBtn.disabled = false;
            generateBtn.querySelector("span").textContent = "Generate Natural Voice Speech";
        }
    });

    // Canvas Waveform Animation
    function drawWaveform() {
        const width = canvas.width = canvas.parentElement.clientWidth;
        const height = canvas.height = 60;
        
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = "#f59e0b";
        
        const bars = 45;
        const barWidth = width / bars - 4;
        
        for (let i = 0; i < bars; i++) {
            const barHeight = Math.random() * (height - 10) + 10;
            const x = i * (barWidth + 4);
            const y = (height - barHeight) / 2;
            
            ctx.beginPath();
            ctx.roundRect(x, y, barWidth, barHeight, 3);
            ctx.fill();
        }
    }
});
