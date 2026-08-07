import express from 'express';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { validExercises } from "./exerciseWhitelist.js";
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
            typeof exercise.tip !== "string"
        ) {
            return false;
        }
        const exists = validExercises.some(
            valid =>
                valid.toLowerCase() === exercise.name.toLowerCase()
        );
        if (!exists) {
            return false;
        }
    }
    return true;
}

  app.post('/api/substitute', async (req, res) => {
  const { exercise, equipment } = req.body;
  // DELIVERABLE CHECKLIST: Centralized Context-Aware Hardcoded Fallback Error Handling
  const muscleGroup = exerciseToMuscle[exercise];
  const fallbackResponse = {
    alternatives: fallbackExercises[muscleGroup]
};

  //Input validation
  if (!exercise || typeof exercise !== "string") {
  return res.status(400).json({
    error: "Please provide a valid exercise."
  });
}

if (!Array.isArray(equipment) || equipment.length === 0) {
  return res.status(400).json({
    error: "Please select at least one equipment option."
  });
}

  try {
    // V2: Highly optimized prompt specifying exact JSON schemas
  const prompt = `You are an expert biomechanics fitness trainer.
The user wanted to perform this exercise: "${exercise}", but the machine is taken.
They only have access to these equipment types right now:
${equipment.join(', ')}
Provide exactly two biomechanically accurate substitute exercises that hit the identical target muscles.
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

    // Call free-tier Gemini Flash model
    const response = await ai.models.generateContent({
      model: 'gemini-2.0-flash',
      contents: prompt,
    });

    const rawText = response.text.trim();
    console.log("Raw AI response:\n", rawText);

    // Strip accidental markdown blocks if the LLM hallucinated them
    const cleanJson = rawText.replace(/```json/g, "").replace(/```/g, "").trim();
    const parsedData = JSON.parse(cleanJson);

    if (!validateAIResponse(parsedData)) {
      console.log("AI validation failed. Using fallback.");
      return res.json(fallbackResponse);
}
      res.json(parsedData);
  } catch (error) {
    console.error("⚠️ System caught an API or parsing exception:", error.message);
    // Return safe fallback response if AI request or parsing fails
    res.json(fallbackResponse);
  }
});

app.listen(PORT, () => {
  console.log(`🚀 AltLift running on http://localhost:${PORT}`);
});
