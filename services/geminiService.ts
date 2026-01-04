
import { GoogleGenAI, Type, Modality } from "@google/genai";

const API_KEY = process.env.API_KEY || "";

export const getGeminiResponse = async (prompt: string, mode: 'fast' | 'think' = 'fast') => {
  const ai = new GoogleGenAI({ apiKey: API_KEY });
  const modelName = mode === 'think' ? 'gemini-3-pro-preview' : 'gemini-3-flash-preview';
  
  const config: any = {
    tools: nbaTools,
  };
  
  if (mode === 'think') {
    config.thinkingConfig = { thinkingBudget: 32768 };
  }

  const response = await ai.models.generateContent({
    model: modelName,
    contents: prompt,
    config
  });

  // Handle simple response. In a full app, we would handle tool calls recursively.
  return response.text;
};

export const getTTSAudio = async (text: string) => {
  const ai = new GoogleGenAI({ apiKey: API_KEY });
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-preview-tts",
    contents: [{ parts: [{ text }] }],
    config: {
      responseModalities: [Modality.AUDIO],
      speechConfig: {
        voiceConfig: {
          prebuiltVoiceConfig: { voiceName: 'Kore' },
        },
      },
    },
  });

  return response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
};

// Expanded Tool declaration for NBA data ecosystem
export const nbaTools = [
  {
    functionDeclarations: [
      {
        name: 'get_nba_player_stats',
        description: 'Fetch real-time or historical NBA player performance statistics.',
        parameters: {
          type: Type.OBJECT,
          properties: {
            playerName: { type: Type.STRING, description: 'The name of the NBA player.' },
            season: { type: Type.STRING, description: 'The season for which to fetch stats (e.g., 2024-25, 2012-13).' }
          },
          required: ['playerName']
        }
      },
      {
        name: 'compare_nba_players',
        description: 'Fetch side-by-side comparison data for two or more NBA players.',
        parameters: {
          type: Type.OBJECT,
          properties: {
            playerNames: { 
              type: Type.ARRAY, 
              items: { type: Type.STRING },
              description: 'List of player names to compare.' 
            },
            season: { type: Type.STRING, description: 'The season to compare (defaults to current).' }
          },
          required: ['playerNames']
        }
      },
      {
        name: 'get_player_career_milestones',
        description: 'Retrieve awards, records, and significant milestones throughout a players career.',
        parameters: {
          type: Type.OBJECT,
          properties: {
            playerName: { type: Type.STRING, description: 'The name of the NBA player.' }
          },
          required: ['playerName']
        }
      }
    ]
  }
];

// Helper for PCM Decoding
export function decodeBase64(base64: string) {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

export async function decodeAudioData(
  data: Uint8Array,
  ctx: AudioContext,
  sampleRate: number = 24000,
  numChannels: number = 1,
): Promise<AudioBuffer> {
  const dataInt16 = new Int16Array(data.buffer);
  const frameCount = dataInt16.length / numChannels;
  const buffer = ctx.createBuffer(numChannels, frameCount, sampleRate);

  for (let channel = 0; channel < numChannels; channel++) {
    const channelData = buffer.getChannelData(channel);
    for (let i = 0; i < frameCount; i++) {
      channelData[i] = dataInt16[i * numChannels + channel] / 32768.0;
    }
  }
  return buffer;
}
