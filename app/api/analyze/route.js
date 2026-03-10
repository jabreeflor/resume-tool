import OpenAI from 'openai';

export const dynamic = 'force-dynamic';

export async function POST(request) {
  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });
  try {
    const { resume } = await request.json();

    if (!resume?.trim()) {
      return Response.json({ error: 'Resume text is required' }, { status: 400 });
    }

    if (!process.env.OPENAI_API_KEY) {
      return Response.json({ error: 'OPENAI_API_KEY not configured' }, { status: 500 });
    }

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: `You are an expert resume reviewer and career coach. Analyze the resume and return a JSON response with two fields:

1. "suggestions" — an array of improvement suggestions, each with:
   - "title": short title
   - "description": detailed explanation  
   - "category": one of "Content", "Formatting", "Language", "Impact", "ATS"
   - "priority": "high", "medium", or "low"
   - "example": (optional) a concrete rewrite example

2. "improved" — a complete improved version of the resume in clean plain text format, incorporating all high-priority suggestions.

Focus on:
- Quantifying achievements (numbers, percentages, dollar amounts)
- Strong action verbs
- ATS-friendly formatting
- Removing filler words and clichés
- Consistent tense and formatting
- Relevant keywords for the industry

Return ONLY valid JSON, no markdown code fences.`,
        },
        {
          role: 'user',
          content: `Please analyze and improve this resume:\n\n${resume}`,
        },
      ],
      temperature: 0.7,
      max_tokens: 4000,
    });

    const content = completion.choices[0]?.message?.content || '';

    // Parse the JSON response, handling potential markdown wrapping
    let parsed;
    try {
      const cleaned = content.replace(/^```json?\n?/i, '').replace(/\n?```$/i, '').trim();
      parsed = JSON.parse(cleaned);
    } catch {
      // If JSON parsing fails, return a basic response
      return Response.json({
        suggestions: [{
          title: 'Analysis Complete',
          description: content,
          category: 'Content',
          priority: 'medium',
        }],
        improved: resume,
      });
    }

    return Response.json({
      suggestions: parsed.suggestions || [],
      improved: parsed.improved || resume,
    });
  } catch (e) {
    console.error('Analysis error:', e);

    if (e.code === 'insufficient_quota') {
      return Response.json({ error: 'OpenAI API quota exceeded. Check billing.' }, { status: 429 });
    }

    return Response.json({ error: e.message || 'Analysis failed' }, { status: 500 });
  }
}
