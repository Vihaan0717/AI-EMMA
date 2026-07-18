// knowledge/mathKnowledge.js

const mathKnowledge = {

  // ============================================
  // ALGEBRA
  // ============================================
  algebra: {
    quadraticFormula: {
      formula: 'x = (-b ± √(b²-4ac)) / 2a',
      description: 'Solves ax² + bx + c = 0',
      example: 'x²+5x+6=0 → x=-2 or x=-3',
      keywords: ['quadratic', 'ax2', 'square equation', 'roots']
    },
    linearEquation: {
      formula: 'y = mx + b',
      description: 'Slope-intercept form',
      example: 'y = 2x + 3',
      keywords: ['linear', 'slope', 'line equation', 'mx+b']
    },
    arithmetic_progression: {
      formula: {
        nth_term: 'aₙ = a + (n-1)d',
        sum: 'Sₙ = n/2 × (2a + (n-1)d)',
        sum_alt: 'Sₙ = n/2 × (a + l)'
      },
      description: 'AP - sequence with common difference',
      example: '2,5,8,11... a=2, d=3',
      keywords: ['AP', 'arithmetic', 'progression', 'sequence', 'series']
    },
    geometric_progression: {
      formula: {
        nth_term: 'aₙ = a × r^(n-1)',
        sum: 'Sₙ = a(rⁿ-1)/(r-1)',
        infinite_sum: 'S∞ = a/(1-r) when |r|<1'
      },
      description: 'GP - sequence with common ratio',
      example: '2,6,18,54... a=2, r=3',
      keywords: ['GP', 'geometric', 'ratio', 'geometric series']
    },
    binomial_theorem: {
      formula: '(a+b)ⁿ = Σ C(n,r) × aⁿ⁻ʳ × bʳ',
      description: 'Expansion of (a+b)^n',
      keywords: ['binomial', 'expansion', 'nCr']
    },
    logarithms: {
      formulas: [
        'log(mn) = log(m) + log(n)',
        'log(m/n) = log(m) - log(n)',
        'log(mⁿ) = n × log(m)',
        'logₐb = log(b)/log(a)',
        'log₁₀(10) = 1',
        'ln(e) = 1'
      ],
      keywords: ['log', 'logarithm', 'ln', 'natural log']
    },
    factoring: {
      formulas: [
        'a²-b² = (a+b)(a-b)',
        'a³+b³ = (a+b)(a²-ab+b²)',
        'a³-b³ = (a-b)(a²+ab+b²)',
        '(a+b)² = a²+2ab+b²',
        '(a-b)² = a²-2ab+b²',
        '(a+b+c)² = a²+b²+c²+2ab+2bc+2ca'
      ],
      keywords: ['factor', 'expand', 'identity', 'algebraic identity']
    }
  },

  // ============================================
  // GEOMETRY
  // ============================================
  geometry: {
    circle: {
      formulas: {
        area: 'A = πr²',
        circumference: 'C = 2πr = πd',
        arc_length: 'L = rθ (θ in radians)',
        sector_area: 'A = (θ/2π) × πr² = r²θ/2'
      },
      keywords: ['circle', 'radius', 'diameter', 'circumference', 'arc']
    },
    triangle: {
      formulas: {
        area: 'A = (1/2) × base × height',
        area_heron: 'A = √(s(s(s-a)(s-b)(s-c)), s=(a+b+c)/2',
        area_trig: 'A = (1/2) × a × b × sin(C)',
        pythagoras: 'a² + b² = c²',
        perimeter: 'P = a + b + c'
      },
      types: {
        equilateral: {
          area: '(√3/4) × a²',
          height: '(√3/2) × a'
        },
        right_triangle: {
          sin: 'opposite/hypotenuse',
          cos: 'adjacent/hypotenuse',
          tan: 'opposite/adjacent'
        }
      },
      keywords: ['triangle', 'area', 'pythagoras', 'hypotenuse', 'heron']
    },
    rectangle: {
      formulas: {
        area: 'A = l × w',
        perimeter: 'P = 2(l + w)',
        diagonal: 'd = √(l² + w²)'
      },
      keywords: ['rectangle', 'length', 'width', 'perimeter']
    },
    sphere: {
      formulas: {
        volume: 'V = (4/3)πr³',
        surface_area: 'SA = 4πr²'
      },
      keywords: ['sphere', 'ball', 'volume sphere', '3d circle']
    },
    cylinder: {
      formulas: {
        volume: 'V = πr²h',
        curved_surface: 'CSA = 2πrh',
        total_surface: 'TSA = 2πr(r+h)'
      },
      keywords: ['cylinder', 'curved surface', 'total surface']
    },
    cone: {
      formulas: {
        volume: 'V = (1/3)πr²h',
        slant_height: 'l = √(r²+h²)',
        curved_surface: 'CSA = πrl',
        total_surface: 'TSA = πr(r+l)'
      },
      keywords: ['cone', 'slant', 'volume cone']
    },
    cube_cuboid: {
      cube: {
        volume: 'V = a³',
        surface_area: 'SA = 6a²',
        diagonal: 'd = a√3'
      },
      cuboid: {
        volume: 'V = l×b×h',
        surface_area: 'SA = 2(lb+bh+hl)',
        diagonal: 'd = √(l²+b²+h²)'
      },
      keywords: ['cube', 'cuboid', 'box volume']
    }
  },

  // ============================================
  // TRIGONOMETRY
  // ============================================
  trigonometry: {
    basic: {
      sin: 'sin(θ) = opposite/hypotenuse',
      cos: 'cos(θ) = adjacent/hypotenuse',
      tan: 'tan(θ) = opposite/adjacent = sin/cos',
      cosec: 'cosec(θ) = 1/sin(θ)',
      sec: 'sec(θ) = 1/cos(θ)',
      cot: 'cot(θ) = 1/tan(θ)',
      keywords: ['sin', 'cos', 'tan', 'trig', 'trigonometry']
    },
    identities: {
      pythagorean: [
        'sin²θ + cos²θ = 1',
        '1 + tan²θ = sec²θ',
        '1 + cot²θ = cosec²θ'
      ],
      compound: [
        'sin(A+B) = sinA.cosB + cosA.sinB',
        'sin(A-B) = sinA.cosB - cosA.sinB',
        'cos(A+B) = cosA.cosB - sinA.sinB',
        'cos(A-B) = cosA.cosB + sinA.sinB',
        'tan(A+B) = (tanA+tanB)/(1-tanA.tanB)'
      ],
      double_angle: [
        'sin(2A) = 2sinA.cosA',
        'cos(2A) = cos²A - sin²A = 1-2sin²A = 2cos²A-1',
        'tan(2A) = 2tanA/(1-tan²A)'
      ],
      keywords: ['identity', 'compound angle', 'double angle', 'trig identity']
    },
    standard_values: {
      '0°':  { sin: 0,    cos: 1,    tan: 0    },
      '30°': { sin: '1/2', cos: '√3/2', tan: '1/√3' },
      '45°': { sin: '1/√2', cos: '1/√2', tan: 1 },
      '60°': { sin: '√3/2', cos: '1/2', tan: '√3' },
      '90°': { sin: 1,    cos: 0,    tan: '∞'  },
      keywords: ['sin 30', 'cos 60', 'tan 45', 'standard values']
    }
  },

  // ============================================
  // CALCULUS
  // ============================================
  calculus: {
    derivatives: {
      basic_rules: [
        'd/dx(c) = 0',
        'd/dx(x) = 1',
        'd/dx(xⁿ) = nxⁿ⁻¹',
        'd/dx(eˣ) = eˣ',
        'd/dx(aˣ) = aˣ.ln(a)',
        'd/dx(ln x) = 1/x',
        'd/dx(sin x) = cos x',
        'd/dx(cos x) = -sin x',
        'd/dx(tan x) = sec²x',
        'd/dx(cot x) = -cosec²x',
        'd/dx(sec x) = sec x.tan x',
        'd/dx(cosec x) = -cosec x.cot x'
      ],
      chain_rule: 'd/dx[f(g(x))] = f\'(g(x)) × g\'(x)',
      product_rule: 'd/dx(uv) = u.dv/dx + v.du/dx',
      quotient_rule: 'd/dx(u/v) = (v.du/dx - u.dv/dx) / v²',
      keywords: ['derivative', 'differentiate', 'dy/dx', 'calculus']
    },
    integrals: {
      basic_rules: [
        '∫xⁿ dx = xⁿ⁺¹/(n+1) + C',
        '∫1/x dx = ln|x| + C',
        '∫eˣ dx = eˣ + C',
        '∫sin x dx = -cos x + C',
        '∫cos x dx = sin x + C',
        '∫sec²x dx = tan x + C',
        '∫cosec²x dx = -cot x + C',
        '∫sec x.tan x dx = sec x + C'
      ],
      by_parts: '∫u.dv = uv - ∫v.du',
      keywords: ['integral', 'integrate', 'antiderivative', 'area under curve']
    },
    limits: {
      standard: [
        'lim(x→0) sin(x)/x = 1',
        'lim(x→0) (1+x)^(1/x) = e',
        'lim(x→∞) (1+1/x)^x = e',
        'lim(x→0) (eˣ-1)/x = 1',
        'lim(x→0) (aˣ-1)/x = ln(a)'
      ],
      keywords: ['limit', 'lim', 'approach', 'tends to']
    }
  },

  // ============================================
  // STATISTICS & PROBABILITY
  // ============================================
  statistics: {
    central_tendency: {
      mean: 'x̄ = Σx/n',
      median: 'Middle value when sorted',
      mode: 'Most frequent value',
      weighted_mean: 'x̄ = Σ(w×x)/Σw',
      keywords: ['mean', 'average', 'median', 'mode', 'central tendency']
    },
    dispersion: {
      range: 'R = Max - Min',
      variance: 'σ² = Σ(x-x̄)²/n',
      std_deviation: 'σ = √(Σ(x-x̄)²/n)',
      coefficient_variation: 'CV = (σ/x̄) × 100%',
      keywords: ['variance', 'standard deviation', 'dispersion', 'spread']
    },
    probability: {
      basic: 'P(A) = Favorable outcomes / Total outcomes',
      addition: 'P(A∪B) = P(A) + P(B) - P(A∩B)',
      multiplication: 'P(A∩B) = P(A) × P(B|A)',
      conditional: 'P(A|B) = P(A∩B) / P(B)',
      complement: 'P(A\') = 1 - P(A)',
      bayes: 'P(A|B) = P(B|A)×P(A) / P(B)',
      keywords: ['probability', 'P(A)', 'chance', 'likelihood', 'bayes']
    },
    distributions: {
      binomial: {
        formula: 'P(X=r) = C(n,r) × pʳ × (1-p)ⁿ⁻ʳ',
        mean: 'μ = np',
        variance: 'σ² = np(1-p)'
      },
      normal: {
        formula: 'f(x) = (1/σ√2π) × e^(-(x-μ)²/2σ²)',
        '68_95_99_rule': '68%-95%-99.7% within 1,2,3 std deviations'
      },
      keywords: ['binomial distribution', 'normal distribution', 'bell curve']
    },
    permutation_combination: {
      permutation: 'P(n,r) = n!/(n-r)!',
      combination: 'C(n,r) = n!/(r!(n-r)!)',
      circular: '(n-1)!',
      keywords: ['permutation', 'combination', 'nPr', 'nCr', 'arrange', 'select']
    }
  },

  // ============================================
  // NUMBER THEORY
  // ============================================
  number_theory: {
    divisibility_rules: {
      2: 'Last digit even',
      3: 'Sum of digits divisible by 3',
      4: 'Last 2 digits divisible by 4',
      5: 'Last digit 0 or 5',
      6: 'Divisible by 2 and 3',
      7: 'Double last digit, subtract from rest',
      8: 'Last 3 digits divisible by 8',
      9: 'Sum of digits divisible by 9',
      10: 'Last digit 0',
      11: 'Alternating sum of digits divisible by 11'
    },
    prime_numbers: {
      definition: 'Divisible only by 1 and itself',
      sieve_of_eratosthenes: 'Algorithm to find all primes',
      fermat_little_theorem: 'aᵖ ≡ a (mod p) where p is prime',
      keywords: ['prime', 'factor', 'divisible', 'LCM', 'HCF', 'GCD']
    },
    hcf_lcm: {
      hcf_formula: 'HCF × LCM = Product of two numbers',
      euclidean: 'HCF(a,b) = HCF(b, a mod b)',
      keywords: ['HCF', 'LCM', 'GCD', 'highest common factor']
    }
  },

  // ============================================
  // MATRICES & DETERMINANTS
  // ============================================
  matrices: {
    operations: {
      addition: '(A+B)ᵢⱼ = Aᵢⱼ + Bᵢⱼ',
      multiplication: '(AB)ᵢⱼ = Σ Aᵢₖ × Bₖⱼ',
      transpose: '(Aᵀ)ᵢⱼ = Aⱼᵢ'
    },
    determinant_2x2: 'det(A) = ad - bc for [[a,b],[c,d]]',
    determinant_3x3: 'Cofactor expansion method',
    inverse: {
      formula: 'A⁻¹ = adj(A) / det(A)',
      condition: 'Exists only if det(A) ≠ 0'
    },
    cramer_rule: 'x = Dₓ/D, y = Dᵧ/D, z = D_z/D',
    keywords: ['matrix', 'determinant', 'inverse', 'eigen', 'cramer']
  },

  // ============================================
  // PHYSICS-MATH FORMULAS
  // ============================================
  physics_math: {
    kinematics: [
      'v = u + at',
      's = ut + (1/2)at²',
      'v² = u² + 2as',
      's = (u+v)/2 × t'
    ],
    mechanics: {
      force: 'F = ma',
      work: 'W = F × d × cosθ',
      power: 'P = W/t',
      energy: 'KE = (1/2)mv², PE = mgh'
    },
    keywords: ['physics', 'kinematics', 'velocity', 'acceleration', 'force']
  },

  // ============================================
  // FINANCIAL MATH
  // ============================================
  financial: {
    simple_interest: {
      formula: 'SI = (P × R × T) / 100',
      amount: 'A = P + SI'
    },
    compound_interest: {
      formula: 'A = P(1 + R/100)ᵀ',
      ci: 'CI = A - P',
      continuous: 'A = Peʳᵗ'
    },
    profit_loss: {
      profit: 'Profit = SP - CP',
      loss: 'Loss = CP - SP',
      profit_percent: 'Profit% = (Profit/CP) × 100',
      loss_percent: 'Loss% = (Loss/CP) × 100',
      sp_from_profit: 'SP = CP × (100 + P%)/100',
      sp_from_loss: 'SP = CP × (100 - L%)/100'
    },
    percentage: {
      formula: 'Percentage = (Part/Whole) × 100',
      increase: 'New = Old × (1 + %/100)',
      decrease: 'New = Old × (1 - %/100)'
    },
    keywords: ['interest', 'SI', 'CI', 'profit', 'loss', 'percentage', 'discount']
  }
};

// ============================================
// MATH PROBLEM DETECTOR
// ============================================
function detectMathQuestion(text) {
  const mathKeywords = [
    // General
    'calculate', 'solve', 'find', 'compute', 'evaluate',
    'what is', 'how much', 'formula', 'equation',
    // Telugu
    'calculate cheseyyi', 'solve cheseyyi', 'formula em',
    'math cheppu', 'calculation cheyyi', 'answer em',
    // Numbers
    /\d+[\+\-\×\÷\*\/]\d+/,
    /\d+\s*[\+\-\*\/]\s*\d+/,
    // Symbols
    '²', '³', '√', 'π', 'Σ', '∫', '∞',
    // Topics
    'quadratic', 'triangle', 'circle', 'probability',
    'derivative', 'integral', 'matrix', 'determinant',
    'sin', 'cos', 'tan', 'log', 'percentage',
    'profit', 'loss', 'interest', 'permutation',
    'combination', 'mean', 'variance', 'statistics'
  ];

  const lowerText = text.toLowerCase();
  return mathKeywords.some(kw => 
    typeof kw === 'string' 
      ? lowerText.includes(kw) 
      : kw.test(text)
  );
}

// Get relevant math formulas
function getRelevantFormulas(text) {
  const lowerText = text.toLowerCase();
  const relevant = [];
  
  function searchSection(section, sectionName) {
    for (const [key, value] of Object.entries(section)) {
      if (key === 'keywords' && Array.isArray(value)) {
        if (value.some(kw => lowerText.includes(kw.toLowerCase()))) {
          relevant.push({ section: sectionName, key, data: section });
        }
      } else if (typeof value === 'object' && !Array.isArray(value)) {
        searchSection(value, sectionName + '.' + key);
      }
    }
  }
  
  for (const [section, data] of Object.entries(mathKnowledge)) {
    searchSection(data, section);
  }
  
  return relevant;
}

module.exports = { 
  mathKnowledge, 
  detectMathQuestion,
  getRelevantFormulas
};
