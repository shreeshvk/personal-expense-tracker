import express from 'express';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { validExercises } from "./exercisewhitelist.js";
import { exerciseToMuscle } from "./exerciseToMuscle.js";
import { fallbackExercises } from "./FallbackAltExercises.js";
import { GoogleGenAI } from '@google/genai';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize Google Gemini Client (will look for process.env.GEMINI_API_KEY automatically)
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });


app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

function validateAIResponse(data) {
  if (!data.alternatives || !Array.isArray(data.alternatives)) {
    return false;
  }
  if (data.alternatives.length !== 2) {
    return false;
  }
  for (const exercise of data.alternatives) {
    if (
      typeof exercise.name !== "string" ||
      typeof exercise.targetMuscle !== "string" ||
      typeof exercise.tip !== "string" ||
      exercise.name.trim().length < 2 ||
      exercise.name.trim().length > 80 ||
      exercise.targetMuscle.trim().length < 3 ||
      exercise.tip.trim().length < 10
    ) {
      return false;
    }
  }
  return true;
}

app.post('/api/substitute', async (req, res) => {
  const { exercise, equipment } = req.body;
  const trimmedExercise = typeof exercise === "string" ? exercise.trim() : "";

  // 1. Upstream Input Validation & Sanitization
  if (!trimmedExercise || !/[a-zA-Z]{2,}/.test(trimmedExercise)) {
    return res.status(400).json({
      error: "Please enter a valid exercise name containing real letters (e.g., Bench Press, Squat, Lat Pulldown)."
    });
  }

  if (!Array.isArray(equipment) || equipment.length === 0) {
    return res.status(400).json({
      error: "Please select at least one available equipment option."
    });
  }

  // Fallback data preparation
  const muscleGroup = exerciseToMuscle[trimmedExercise];
  const fallbackResponse = {
    alternatives: fallbackExercises[muscleGroup] || [
      {
        name: "Bodyweight Push-up",
        targetMuscle: "Chest, Shoulders, Triceps",
        tip: "Keep a rigid core plank and lower your chest under control to roughly 90 degrees elbow bend."
      },
      {
        name: "Bodyweight Squat",
        targetMuscle: "Quadriceps, Glutes, Hamstrings",
        tip: "Maintain a neutral spine and sit back into your hips while driving knees outward over your toes."
      }
    ]
  };

  try {
    // V3: Enhanced prompt with adversarial detection & movement diversity mandate
    const prompt = `You are an expert biomechanics fitness trainer.
The user requested substitute exercises for: "${trimmedExercise}".
Available equipment: ${equipment.join(', ')}.

STRICT INSTRUCTIONS:
1. FIRST EVALUATION: Is "${trimmedExercise}" a real workout exercise, common exercise variation, or valid fitness abbreviation/slang?
   - If "${trimmedExercise}" is non-exercise text, fake/joke exercise (e.g., "Pizza Pressing", "Hello", "test"), or meaningless input, you MUST return exclusively this JSON:
   {"invalidExercise": true, "error": "\"${trimmedExercise}\" is not a recognized exercise. Please enter a valid workout exercise."}

2. MOVEMENT DIVERSITY MANDATE: If it IS a valid exercise, provide exactly TWO biomechanically accurate substitute exercises that hit identical target muscles.
   - The two exercises MUST utilize distinctly different movement patterns or setups (e.g., one bilateral compound/isolation and one unilateral movement, or two distinctly different angles).
   - Do NOT provide two minor variations of the exact same exercise (e.g., do NOT give both Back Squat and Front Squat with resistance bands).

Return your response exclusively as a valid JSON object matching this exact format:
{
  "alternatives": [
    {
      "name": "Exercise Title",
      "targetMuscle": "Muscle Groups Targeted",
      "tip": "One explicit mechanical execution form tip."
    }
  ]
}
Do not include any introductory text, markdown wrappers, backticks, or explanation outside the JSON object.`;

    // Call Gemini API with automatic model fallback if quota is exceeded
    const candidateModels = ['gemini-flash-latest', 'gemini-flash-lite-latest', 'gemini-2.0-flash-lite'];
    let response;
    let lastError;

    for (const modelName of candidateModels) {
      try {
        response = await ai.models.generateContent({
          model: modelName,
          contents: prompt,
        });
        if (response && response.text) break;
      } catch (err) {
        lastError = err;
        console.warn(`⚠️ Model ${modelName} quota/error: ${err.message.substring(0, 120)}. Trying fallback model...`);
      }
    }

    if (!response || !response.text) {
      throw lastError || new Error("All AI models failed or exceeded quota.");
    }

    const rawText = response.text.trim();
    console.log("Raw AI response:\n", rawText);

    // Strip accidental markdown blocks if the LLM hallucinated them
    const cleanJson = rawText.replace(/```json/g, "").replace(/```/g, "").trim();
    const parsedData = JSON.parse(cleanJson);

    // Check if AI detected invalid/fake exercise
    if (parsedData.invalidExercise) {
      console.log(`Unrecognized exercise input caught: "${trimmedExercise}"`);
      return res.status(400).json({
        error: parsedData.error || `"${trimmedExercise}" is not a recognized exercise. Please enter a valid workout exercise.`
      });
    }

    if (!validateAIResponse(parsedData)) {
      console.log("AI validation failed. Using fallback.");
      return res.json(fallbackResponse);
    }
    res.json(parsedData);
  } catch (error) {
    console.error("⚠️ System caught an API or parsing exception:", error.message);
    res.json(fallbackResponse);
  }
});

app.listen(PORT, () => {
  console.log(`🚀 AltLift running on http://localhost:${PORT}`);
});
