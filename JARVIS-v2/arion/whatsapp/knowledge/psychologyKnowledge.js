// knowledge/psychologyKnowledge.js

const psychologyKnowledge = {

  // ============================================
  // 1. COGNITIVE PSYCHOLOGY
  // ============================================
  cognitive: {
    cognitive_biases: {
      confirmation_bias: {
        definition: 'Tendency to search for info that confirms existing beliefs',
        example: 'Only reading news that agrees with your views',
        how_to_detect: 'When someone only agrees with one-sided info',
        counter: 'Present opposing evidence gently'
      },
      availability_heuristic: {
        definition: 'Judging probability by how easily examples come to mind',
        example: 'Fearing plane crash more than car crash after seeing news',
        how_to_detect: 'Overestimating rare events after news coverage',
        counter: 'Show actual statistics'
      },
      dunning_kruger: {
        definition: 'Unskilled people overestimate ability; skilled underestimate',
        example: 'Beginner thinks they know everything; expert feels unsure',
        how_to_detect: 'Overconfidence with little knowledge',
        counter: 'Encourage learning and humility'
      },
      anchoring_bias: {
        definition: 'Over-relying on first information received',
        example: 'First price seen influences all future price judgments',
        how_to_detect: 'Stuck on initial numbers/opinions',
        counter: 'Present multiple reference points'
      },
      sunk_cost_fallacy: {
        definition: 'Continuing something because of past investment, not future value',
        example: 'Staying in bad relationship because already invested years',
        how_to_detect: "Phrases like 'but I've already...'",
        counter: 'Focus on future outcomes only'
      },
      halo_effect: {
        definition: 'One positive trait influences overall judgment',
        example: 'Attractive people judged as more intelligent/honest',
        how_to_detect: 'Judging whole person by one feature',
        counter: 'Evaluate each trait separately'
      },
      recency_bias: {
        definition: 'Giving more weight to recent events',
        example: 'Judging whole friendship by last fight',
        how_to_detect: 'Ignoring history, focusing on recent',
        counter: 'Look at full history and pattern'
      }
    },
    
    memory: {
      types: {
        short_term: 'Holds ~7 items for 20-30 seconds',
        long_term: 'Unlimited capacity, permanent storage',
        working_memory: 'Active manipulation of information',
        episodic: 'Personal experiences and events',
        semantic: 'Facts and general knowledge',
        procedural: 'How to do things (riding bike)'
      },
      forgetting_curve: 'Ebbinghaus: 70% forgotten in 24hrs without review',
      spaced_repetition: 'Review at increasing intervals to retain',
      memory_palace: 'Associate info with familiar locations',
      keywords: ['memory', 'forget', 'remember', 'recall', 'study']
    },
    
    learning: {
      styles: {
        visual: 'Learn through images, diagrams, charts',
        auditory: 'Learn through listening and speaking',
        reading_writing: 'Learn through reading and notes',
        kinesthetic: 'Learn through doing and experience'
      },
      techniques: {
        pomodoro: '25min focus + 5min break cycles',
        feynman: 'Teach it simply to understand deeply',
        active_recall: 'Test yourself instead of re-reading',
        mind_mapping: 'Connect ideas visually',
        chunking: 'Group information into meaningful units'
      },
      keywords: ['learn', 'study', 'remember', 'memorize', 'understand']
    }
  },

  // ============================================
  // 2. BEHAVIORAL PSYCHOLOGY
  // ============================================
  behavioral: {
    conditioning: {
      classical: {
        definition: 'Pavlov - associating neutral stimulus with response',
        example: 'Dog salivates at bell (associated with food)',
        application: 'Phobias, emotional responses, habits'
      },
      operant: {
        definition: 'Skinner - behavior shaped by consequences',
        positive_reinforcement: 'Add reward to increase behavior',
        negative_reinforcement: 'Remove unpleasant to increase behavior',
        positive_punishment: 'Add unpleasant to decrease behavior',
        negative_punishment: 'Remove reward to decrease behavior',
        keywords: ['reward', 'punishment', 'reinforce', 'conditioning']
      }
    },
    
    habits: {
      habit_loop: 'Cue → Routine → Reward (Charles Duhigg)',
      formation_time: 'Average 66 days to form a habit',
      breaking_habits: 'Identify cue, change routine, keep reward',
      keystone_habits: 'Core habits that trigger other good habits',
      implementation_intention: "If-then planning: 'If X then I'll do Y'",
      keywords: ['habit', 'routine', 'discipline', 'change behavior']
    },
    
    motivation: {
      maslow_hierarchy: {
        level1: 'Physiological (food, water, shelter)',
        level2: 'Safety (security, stability)',
        level3: 'Social (belonging, love)',
        level4: 'Esteem (respect, achievement)',
        level5: 'Self-actualization (reaching potential)'
      },
      intrinsic_vs_extrinsic: {
        intrinsic: 'Motivated by internal satisfaction',
        extrinsic: 'Motivated by external rewards/punishments',
        insight: 'Intrinsic motivation leads to deeper learning'
      },
      self_determination: 'Autonomy + Competence + Relatedness = Motivation',
      keywords: ['motivation', 'drive', 'inspire', 'goal', 'achieve']
    }
  },

  // ============================================
  // 3. SOCIAL PSYCHOLOGY
  // ============================================
  social: {
    influence: {
      cialdini_principles: {
        reciprocity: 'People feel obliged to return favors',
        commitment: 'People honor prior commitments (consistency)',
        social_proof: "People follow what others do ('everyone does it')",
        authority: 'People trust experts and authority figures',
        liking: 'People say yes to people they like',
        scarcity: 'Things seem valuable when limited',
        unity: 'Shared identity increases influence'
      },
      keywords: ['persuade', 'convince', 'influence', 'social proof', 'authority']
    },
    
    communication: {
      active_listening: {
        skills: [
          'Maintain eye contact',
          'Nod and give verbal cues',
          'Reflect back what you heard',
          'Ask clarifying questions',
          'Avoid interrupting',
          'Summarize what was said'
        ]
      },
      nonverbal: {
        body_language: '55% of communication',
        tone_voice: '38% of communication',
        words: '7% of communication (Mehrabian)',
        open_posture: 'Arms uncrossed = approachable',
        mirroring: 'Copy body language = builds rapport'
      },
      difficult_conversations: {
        steps: [
          '1. Choose right time and place',
          '2. Start with curiosity not blame',
          '3. Use "I feel" not "You always"',
          '4. Listen to understand not respond',
          '5. Find common ground',
          '6. Agree on next steps'
        ]
      },
      keywords: ['communicate', 'talk', 'conversation', 'listen', 'body language']
    },
    
    group_dynamics: {
      groupthink: 'Desire for harmony overrides critical thinking',
      social_loafing: 'Less effort in group vs alone',
      bystander_effect: 'Less likely to help when others present',
      conformity: 'Asch - people conform to group even when wrong',
      obedience: 'Milgram - obey authority figures dangerously',
      keywords: ['group', 'team', 'conform', 'peer pressure', 'social']
    }
  },

  // ============================================
  // 4. EMOTIONAL PSYCHOLOGY
  // ============================================
  emotional: {
    emotional_intelligence: {
      components: {
        self_awareness: 'Knowing your own emotions',
        self_regulation: 'Managing your emotions',
        motivation: 'Using emotions to achieve goals',
        empathy: "Understanding others' emotions",
        social_skills: 'Managing relationships'
      },
      eq_vs_iq: 'EQ predicts success better than IQ in most areas',
      developing_eq: [
        'Name your emotions specifically',
        'Practice mindfulness',
        'Seek feedback',
        'Practice empathy daily',
        'Manage stress proactively'
      ],
      keywords: ['EQ', 'emotional intelligence', 'empathy', 'emotions']
    },
    
    emotions: {
      basic_emotions: ['Joy', 'Sadness', 'Fear', 'Anger', 'Surprise', 'Disgust'],
      plutchik_wheel: '8 primary + 8 secondary emotions in wheel',
      emotion_regulation: {
        reappraisal: 'Reframe situation to change emotional response',
        suppression: 'Hiding emotions (less healthy)',
        acceptance: 'Acknowledge without judgment',
        distraction: 'Focus on something else temporarily'
      },
      keywords: ['emotion', 'feeling', 'mood', 'angry', 'sad', 'happy', 'fear']
    },
    
    grief: {
      kubler_ross_stages: [
        '1. Denial',
        '2. Anger', 
        '3. Bargaining',
        '4. Depression',
        '5. Acceptance'
      ],
      note: 'Not linear - people move between stages',
      keywords: ['grief', 'loss', 'death', 'breakup', 'sad', 'mourn']
    }
  },

  // ============================================
  // 5. PERSONALITY PSYCHOLOGY
  // ============================================
  personality: {
    big_five: {
      openness: 'Curiosity, creativity, open to new experiences',
      conscientiousness: 'Organized, disciplined, goal-oriented',
      extraversion: 'Sociable, energetic, talkative',
      agreeableness: 'Cooperative, trusting, empathetic',
      neuroticism: 'Emotional instability, anxiety, moodiness',
      acronym: 'OCEAN',
      keywords: ['personality', 'OCEAN', 'big five', 'introvert', 'extrovert']
    },
    
    mbti: {
      dimensions: {
        EI: 'Extraversion vs Introversion',
        SN: 'Sensing vs Intuition',
        TF: 'Thinking vs Feeling',
        JP: 'Judging vs Perceiving'
      },
      types: 16,
      note: 'MBTI is popular but limited scientific validity',
      keywords: ['MBTI', 'personality type', 'INFJ', 'ENTJ', 'introvert']
    },
    
    dark_triad: {
      narcissism: 'Excessive self-admiration, entitlement',
      machiavellianism: 'Manipulation, strategic thinking',
      psychopathy: 'Lack of empathy, impulsive',
      detection: [
        'Constant need for admiration',
        'Lacks empathy consistently',
        'Manipulates without guilt',
        'Lies easily and often',
        'Exploits others'
      ],
      keywords: ['narcissist', 'manipulation', 'dark triad', 'toxic person']
    }
  },

  // ============================================
  // 6. MENTAL HEALTH
  // ============================================
  mental_health: {
    anxiety: {
      symptoms: [
        'Excessive worry',
        'Restlessness',
        'Physical tension',
        'Sleep problems',
        'Difficulty concentrating',
        'Avoidance behaviors'
      ],
      cbt_techniques: [
        'Challenge negative thoughts',
        'Behavioral activation',
        'Exposure therapy',
        'Relaxation techniques'
      ],
      immediate_help: [
        '4-7-8 breathing: Inhale 4s, Hold 7s, Exhale 8s',
        '5-4-3-2-1 grounding: 5 see, 4 touch, 3 hear, 2 smell, 1 taste',
        'Progressive muscle relaxation'
      ],
      keywords: ['anxiety', 'worry', 'stress', 'panic', 'nervous', 'tension']
    },
    
    depression: {
      symptoms: [
        'Persistent sadness',
        'Loss of interest',
        'Changes in sleep/appetite',
        'Fatigue',
        'Difficulty concentrating',
        'Feelings of worthlessness'
      ],
      approaches: [
        'Behavioral activation (do things even when unmotivated)',
        'Social connection',
        'Exercise (as effective as antidepressants for mild-moderate)',
        'Sleep hygiene',
        'Professional help'
      ],
      keywords: ['depression', 'depressed', 'hopeless', 'worthless', 'no energy']
    },
    
    stress_management: {
      techniques: {
        mindfulness: 'Present moment awareness without judgment',
        meditation: '10 mins/day reduces cortisol by 20%',
        exercise: 'Natural mood booster - releases endorphins',
        journaling: 'Write thoughts to process emotions',
        social_support: 'Talk to trusted person',
        time_management: 'Prioritize, delegate, eliminate'
      },
      stress_response: 'Fight-Flight-Freeze - cortisol and adrenaline',
      keywords: ['stress', 'overwhelmed', 'burnout', 'tired', 'exhausted']
    }
  },

  // ============================================
  // 7. RELATIONSHIP PSYCHOLOGY
  // ============================================
  relationships: {
    attachment_styles: {
      secure: 'Comfortable with intimacy and independence',
      anxious: 'Fear of abandonment, needs reassurance',
      avoidant: 'Values independence, uncomfortable with closeness',
      disorganized: 'Mixed - both wants and fears intimacy',
      keywords: ['attachment', 'relationship style', 'fear abandonment']
    },
    
    love_languages: {
      words_of_affirmation: 'Verbal compliments and appreciation',
      acts_of_service: 'Doing helpful things',
      receiving_gifts: 'Thoughtful presents',
      quality_time: 'Undivided focused attention',
      physical_touch: 'Hugs, pats, physical presence',
      keywords: ['love language', 'relationship', 'couple', 'partner']
    },
    
    gottman_four_horsemen: {
      criticism: 'Attacking character (bad) vs complaining about behavior',
      contempt: 'Most destructive - eye-rolling, sarcasm, mockery',
      defensiveness: 'Counter-attack instead of taking responsibility',
      stonewalling: 'Shutting down, withdrawing from interaction',
      antidotes: {
        criticism: 'Gentle startup with "I" statements',
        contempt: 'Build culture of appreciation',
        defensiveness: 'Take responsibility for part of problem',
        stonewalling: 'Take breaks, self-soothe'
      },
      keywords: ['relationship problems', 'fight', 'argue', 'conflict', 'divorce']
    },
    
    trust: {
      brene_brown_BRAVING: {
        B: 'Boundaries - respect them',
        R: 'Reliability - do what you say',
        A: 'Accountability - own mistakes',
        V: 'Vault - keep confidences',
        I: 'Integrity - choose courage over comfort',
        N: 'Non-judgment - ask for help',
        G: 'Generosity - assume best intent'
      },
      keywords: ['trust', 'betrayal', 'honest', 'loyal', 'reliable']
    }
  },

  // ============================================
  // 8. HUMAN BEHAVIOR PATTERNS (Chat Analysis)
  // ============================================
  chat_psychology: {
    reading_messages: {
      short_replies: 'May indicate disinterest, busyness, or discomfort',
      delayed_replies: 'Could mean busy, avoiding, or thinking',
      one_word_answers: 'Closed off, not wanting to engage',
      long_messages: 'Interested, wants connection, processing emotions',
      emojis_only: 'Keeping it light, avoiding real conversation',
      seen_no_reply: 'Could be avoidance, overwhelm, or forgot'
    },
    
    manipulation_detection: {
      gaslighting: 'Making you doubt your own reality/memory',
      love_bombing: 'Overwhelming affection to gain control',
      silent_treatment: 'Emotional withdrawal as punishment',
      guilt_tripping: 'Making you feel responsible for their emotions',
      triangulation: 'Using third person to create jealousy/insecurity',
      hot_cold: 'Alternating affection and withdrawal to create attachment',
      keywords: ['manipulation', 'toxic', 'gaslighting', 'control', 'abuse']
    },
    
    conversational_patterns: {
      mirroring: 'Matching language style builds rapport',
      validation: 'Acknowledge feelings before giving advice',
      open_questions: 'Use "how" and "what" to open conversation',
      pacing_leading: 'Match then gradually shift their emotional state',
      future_pacing: 'Help them visualize positive outcomes'
    }
  },

  // ============================================
  // 9. POSITIVE PSYCHOLOGY
  // ============================================
  positive: {
    seligman_perma: {
      P: 'Positive Emotions - joy, gratitude, love',
      E: 'Engagement - flow state, using strengths',
      R: 'Relationships - positive connections',
      M: 'Meaning - belonging to something bigger',
      A: 'Achievement - pursuing goals',
      keywords: ['wellbeing', 'happiness', 'flourish', 'PERMA', 'positive']
    },
    
    flow_state: {
      definition: 'Complete absorption in challenging activity',
      conditions: 'Clear goals + immediate feedback + skill-challenge balance',
      trigger: 'Challenge should be ~4% above current skill level',
      keywords: ['flow', 'zone', 'focus', 'deep work', 'absorbed']
    },
    
    growth_mindset: {
      fixed_mindset: 'Intelligence/talent is fixed',
      growth_mindset: 'Intelligence/talent can be developed',
      language_shift: {
        'I cant do this': "I can't do this YET",
        'Im not smart enough': 'What can I learn here?',
        'I failed': 'What did I learn from this?'
      },
      keywords: ['mindset', 'growth', 'fixed mindset', 'carol dweck', 'potential']
    },
    
    resilience: {
      definition: 'Ability to bounce back from adversity',
      factors: [
        'Strong relationships',
        'Sense of purpose',
        'Positive self-view',
        'Problem-solving skills',
        'Ability to manage emotions'
      ],
      post_traumatic_growth: 'Positive change after struggle - stronger than before',
      keywords: ['resilience', 'bounce back', 'recover', 'strong', 'survive']
    }
  },

  // ============================================
  // 10. TELUGU PSYCHOLOGY (Cultural Context)
  // ============================================
  telugu_psychology: {
    cultural_values: {
      family_collectivism: 'Family decisions over individual',
      respect_hierarchy: 'Elders, teachers, authority respected',
      hospitality: 'Guest is God - Atithi Devo Bhava',
      joint_family_dynamics: 'Multiple generations, shared resources',
      marriage_pressure: 'Cultural expectation at certain age'
    },
    
    communication_style: {
      indirect_communication: 'Often hint rather than state directly',
      saving_face: 'Avoid embarrassing others publicly',
      consensus_building: 'Get everyone to agree before acting',
      emotional_expression: 'More expressive than many cultures'
    },
    
    common_stressors: {
      exam_pressure: 'JEE, NEET, EAMCET stress common',
      job_pressure: 'IT jobs, placement pressure',
      marriage_pressure: 'Age-based marriage expectations',
      financial_family_responsibility: 'Supporting family financially',
      comparison_culture: 'Comparing with neighbors/relatives'
    },
    
    motivational_in_telugu: {
      when_stressed: [
        'Ee situation temporary ra, nuvvu strong vaadu',
        'Chala rojulu kasht padav, ippudu result osthundi',
        'Failure ante end kaadu, next try ki preparation',
        'Nuvvu alone kadhu, everyone faces this'
      ],
      when_sad: [
        'Ee pain real, feel cheyyochu, okay undi',
        'Time anni heal chestundi',
        'Matladali ante cheppu, vinthanu'
      ]
    },
    
    keywords: ['tension', 'pressure', 'exam stress', 'family problem', 
               'marriage', 'job', 'depressed ra', 'sad ga undi']
  }
};

// ============================================
// PSYCHOLOGY DETECTOR
// ============================================
function detectPsychologyContext(text) {
  const lowerText = text.toLowerCase();
  
  const psychKeywords = [
    // Emotions
    'sad', 'happy', 'angry', 'scared', 'worried', 'stressed',
    'depressed', 'anxious', 'lonely', 'confused', 'hurt',
    // Telugu emotions
    'dukkham', 'kopam', 'bhayam', 'tension', 'sad ga undi',
    'chala tension', 'em cheyyalo teliadu', 'alone ga undi',
    // Relationships
    'relationship', 'girlfriend', 'boyfriend', 'wife', 'husband',
    'friend', 'family', 'parents', 'fight', 'breakup',
    // Behavior
    'why do i', 'why does', 'understand', 'behavior', 'habit',
    'cant stop', 'keep doing', 'pattern',
    // Mental health
    'anxiety', 'depression', 'mental health', 'therapy',
    'counseling', 'help me', 'dont know what to do'
  ];
  
  return psychKeywords.some(kw => lowerText.includes(kw));
}

// Get psychology insights for context
function getPsychInsight(text, intent) {
  const lowerText = text.toLowerCase();
  
  // Detect manipulation patterns
  if (lowerText.includes('ignoring') || lowerText.includes('silent treatment')) {
    return psychologyKnowledge.relationships.gottman_four_horsemen.antidotes;
  }
  
  // Detect stress
  if (lowerText.includes('stress') || lowerText.includes('tension') || 
      lowerText.includes('overwhelm')) {
    return psychologyKnowledge.mental_health.stress_management.techniques;
  }
  
  // Detect learning context
  if (lowerText.includes('study') || lowerText.includes('learn') || 
      lowerText.includes('exam')) {
    return psychologyKnowledge.cognitive.learning.techniques;
  }
  
  return null;
}

module.exports = { 
  psychologyKnowledge, 
  detectPsychologyContext,
  getPsychInsight
};
