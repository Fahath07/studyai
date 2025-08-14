"""
Quiz Generator Module for StudyMate AI

This module provides functionality to generate multiple choice questions (MCQs)
from document content for viva exam preparation.
"""

import logging
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCQOption:
    """Represents a single multiple choice option."""
    text: str
    is_correct: bool
    explanation: Optional[str] = None


@dataclass
class MCQuestion:
    """Represents a multiple choice question."""
    question: str
    options: List[MCQOption]
    difficulty: str  # "easy", "medium", "hard"
    topic: str
    explanation: str
    source_context: str


@dataclass
class QuizSession:
    """Represents a quiz session."""
    session_id: str
    questions: List[MCQuestion]
    user_answers: Dict[int, int]  # question_index -> selected_option_index
    start_time: datetime
    end_time: Optional[datetime] = None
    score: Optional[int] = None
    total_questions: Optional[int] = None


def create_mcq_prompt_openai(context: str, num_questions: int = 5, difficulty: str = "medium", topic_focus: str = "") -> str:
    """
    Create a prompt for generating MCQs using OpenAI models with dynamic content.

    Args:
        context: Document content to generate questions from
        num_questions: Number of questions to generate
        difficulty: Difficulty level (easy, medium, hard)
        topic_focus: Optional specific topic to focus on

    Returns:
        str: Formatted prompt for OpenAI
    """

    # Difficulty-specific instructions
    difficulty_instructions = {
        "easy": "Focus on basic concepts, definitions, and simple recall. Use clear, straightforward language.",
        "medium": "Include analytical questions requiring understanding of relationships, applications, and comparisons.",
        "hard": "Create complex questions involving analysis, synthesis, evaluation, and advanced problem-solving."
    }

    # Topic focus instruction
    topic_instruction = f"\n- Focus specifically on: {topic_focus}" if topic_focus else ""

    prompt = f"""You are an expert educator creating UNIQUE multiple choice questions for viva exam preparation. Generate {num_questions} DIFFERENT high-quality questions based SPECIFICALLY on the provided document content.

CRITICAL REQUIREMENTS:
- Questions MUST be directly based on the specific content provided below
- DO NOT use generic questions that could apply to any document
- Extract specific facts, concepts, examples, and details from the document
- Reference specific names, dates, processes, or examples mentioned in the content
- Use EXACT terminology, syntax, keywords, and concepts from the document
- Questions should reference specific sections, code examples, or explanations from the content
- Difficulty level: {difficulty} - {difficulty_instructions.get(difficulty, "")}
- Each question should have exactly 4 options (A, B, C, D)
- Only ONE option should be correct
- Questions should test understanding of the SPECIFIC document content
- Include a brief explanation referencing the document content
- Generate DIFFERENT questions each time, focusing on different parts of the document
- If the document contains code, syntax, or technical terms, use them in questions{topic_instruction}
- Vary question types (definition, application, comparison, analysis) but always document-specific

RESPONSE FORMAT (JSON):
{{
    "questions": [
        {{
            "question": "What is the primary purpose of Python keywords?",
            "options": [
                {{"text": "To define variable names", "is_correct": false}},
                {{"text": "To define coding syntax and structure", "is_correct": true}},
                {{"text": "To create comments in code", "is_correct": false}},
                {{"text": "To import external libraries", "is_correct": false}}
            ],
            "difficulty": "{difficulty}",
            "topic": "Python Basics",
            "explanation": "Python keywords are reserved words that define the syntax and structure of the Python language. They cannot be used as identifiers."
        }}
    ]
}}

CONTENT:
{context}

Generate {num_questions} questions in the exact JSON format shown above:"""
    
    return prompt


def create_mcq_prompt_gemini(context: str, num_questions: int = 5, difficulty: str = "medium", topic_focus: str = "") -> str:
    """
    Create a prompt for generating MCQs using Gemini models with dynamic content.

    Args:
        context: Document content to generate questions from
        num_questions: Number of questions to generate
        difficulty: Difficulty level (easy, medium, hard)
        topic_focus: Optional specific topic to focus on

    Returns:
        str: Formatted prompt for Gemini
    """

    # Difficulty-specific instructions
    difficulty_instructions = {
        "easy": "Focus on basic concepts, definitions, and simple recall.",
        "medium": "Include analytical questions requiring understanding of relationships and applications.",
        "hard": "Create complex questions involving analysis, synthesis, and advanced problem-solving."
    }

    # Topic focus instruction
    topic_instruction = f"\n- Focus specifically on: {topic_focus}" if topic_focus else ""

    prompt = f"""You are an expert educator creating UNIQUE multiple choice questions for viva exam preparation. Generate {num_questions} DIFFERENT high-quality questions based SPECIFICALLY on the provided document content.

CRITICAL REQUIREMENTS:
- Questions MUST be directly based on the specific content provided below
- DO NOT use generic questions that could apply to any document
- Extract specific facts, concepts, examples, and details from the document
- Reference specific names, dates, processes, or examples mentioned in the content
- Use EXACT terminology, syntax, keywords, and concepts from the document
- Questions should reference specific sections, code examples, or explanations from the content
- Difficulty level: {difficulty} - {difficulty_instructions.get(difficulty, "")}
- Each question should have exactly 4 options (A, B, C, D)
- Only ONE option should be correct
- Questions should test understanding of the SPECIFIC document content
- Include a brief explanation referencing the document content
- Generate DIFFERENT questions each time, focusing on different parts of the document
- If the document contains code, syntax, or technical terms, use them in questions{topic_instruction}
- Vary question types and approaches but always document-specific

RESPONSE FORMAT (JSON):
{{
    "questions": [
        {{
            "question": "What is the primary purpose of Python keywords?",
            "options": [
                {{"text": "To define variable names", "is_correct": false}},
                {{"text": "To define coding syntax and structure", "is_correct": true}},
                {{"text": "To create comments in code", "is_correct": false}},
                {{"text": "To import external libraries", "is_correct": false}}
            ],
            "difficulty": "{difficulty}",
            "topic": "Python Basics",
            "explanation": "Python keywords are reserved words that define the syntax and structure of the Python language. They cannot be used as identifiers."
        }}
    ]
}}

CONTENT:
{context[:2500]}

IMPORTANT: Respond with ONLY valid JSON. No additional text before or after. Generate {num_questions} questions in the exact JSON format shown above:"""

    return prompt


def parse_mcq_response(response_text: str) -> List[MCQuestion]:
    """
    Parse AI response and extract MCQ questions.

    Args:
        response_text: Raw response from AI model

    Returns:
        List[MCQuestion]: Parsed questions
    """
    try:
        # Try to extract JSON from response
        response_text = response_text.strip()

        # Find JSON content between ```json and ``` or just raw JSON
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end == -1:  # No closing ```
                json_text = response_text[start:].strip()
            else:
                json_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            if end == -1:  # No closing ```
                json_text = response_text[start:].strip()
            else:
                json_text = response_text[start:end].strip()
        else:
            json_text = response_text

        # Clean up common JSON issues
        json_text = json_text.replace('\n', ' ').replace('\r', '')

        # Try to fix incomplete JSON by finding the last complete question
        if not json_text.endswith('}'):
            # Find the last complete question block
            last_complete = json_text.rfind('}')
            if last_complete != -1:
                # Find the questions array end
                questions_end = json_text.rfind(']', 0, last_complete + 1)
                if questions_end != -1:
                    json_text = json_text[:questions_end + 1] + '}}'

        # Parse JSON
        data = json.loads(json_text)
        questions = []

        for q_data in data.get("questions", []):
            # Skip incomplete questions
            if not q_data.get("question") or not q_data.get("options"):
                continue

            options = []
            for opt_data in q_data.get("options", []):
                if not opt_data.get("text"):  # Skip empty options
                    continue
                option = MCQOption(
                    text=opt_data.get("text", ""),
                    is_correct=opt_data.get("is_correct", False)
                )
                options.append(option)

            # Only add questions with at least 2 options
            if len(options) >= 2:
                question = MCQuestion(
                    question=q_data.get("question", ""),
                    options=options,
                    difficulty=q_data.get("difficulty", "medium"),
                    topic=q_data.get("topic", "General"),
                    explanation=q_data.get("explanation", ""),
                    source_context=""
                )
                questions.append(question)

        return questions

    except Exception as e:
        logger.error(f"Failed to parse MCQ response: {e}")
        logger.error(f"Response text: {response_text[:500]}...")  # Only log first 500 chars
        return []


def generate_mcqs_with_ai(ai_client, context: str, num_questions: int = 5,
                         difficulty: str = "medium", topic_focus: str = "") -> List[MCQuestion]:
    """
    Generate MCQs using the specified AI client.

    Args:
        ai_client: AI client (OpenAI, Gemini, etc.)
        context: Document content to generate questions from
        num_questions: Number of questions to generate
        difficulty: Difficulty level

    Returns:
        List[MCQuestion]: Generated questions
    """
    try:
        logger.info(f"AI Client type: {type(ai_client)}")
        logger.info(f"Context length: {len(context)} characters")

        # Determine client type and create appropriate prompt
        if hasattr(ai_client, 'client') and 'openai' in str(type(ai_client.client)).lower():
            logger.info("Using OpenAI client for MCQ generation")
            from openai_integration import query_openai
            prompt = create_mcq_prompt_openai(context, num_questions, difficulty, topic_focus)
            result = query_openai(ai_client, "", prompt)  # Empty context since prompt contains everything

        elif hasattr(ai_client, 'model') and hasattr(ai_client, 'config'):
            logger.info("Using Gemini client for MCQ generation")
            from gemini_integration import query_gemini
            prompt = create_mcq_prompt_gemini(context, num_questions, difficulty, topic_focus)
            result = query_gemini(ai_client, "", prompt)  # Empty context since prompt contains everything

        elif hasattr(ai_client, 'base_url') and 'openrouter' in str(ai_client.base_url):
            logger.info("Using OpenRouter client for MCQ generation")
            from openrouter_integration import generate_mcqs_with_openrouter
            result = {"success": True, "response": generate_mcqs_with_openrouter(ai_client, context, num_questions, difficulty, topic_focus)}

        else:
            logger.info("Using fallback client for MCQ generation")
            # Fallback for other clients
            from watsonx_integration import query_watsonx
            prompt = create_mcq_prompt_openai(context, num_questions, difficulty, topic_focus)  # Use OpenAI format as default
            result = query_watsonx(ai_client, "", prompt)

        if result.get("success") and result.get("response"):
            questions = parse_mcq_response(result["response"])

            # If parsing failed, try fallback generation
            if not questions:
                logger.warning("JSON parsing failed, trying document-specific fallback generation")
                questions = generate_document_specific_questions(context, num_questions, difficulty, topic_focus)

            logger.info(f"Generated {len(questions)} MCQ questions")
            return questions
        else:
            logger.error(f"Failed to generate MCQs: {result.get('error', 'Unknown error')}")
            # Try document-specific fallback generation
            return generate_document_specific_questions(context, num_questions, difficulty, topic_focus)

    except Exception as e:
        logger.error(f"Error generating MCQs: {e}")
        # Try document-specific fallback generation
        return generate_document_specific_questions(context, num_questions, difficulty, topic_focus)


def generate_document_specific_questions(context: str, num_questions: int = 5,
                                       difficulty: str = "medium", topic_focus: str = "") -> List[MCQuestion]:
    """
    Generate document-specific questions based on actual content.

    Args:
        context: Document content
        num_questions: Number of questions to generate
        difficulty: Difficulty level (easy, medium, hard)
        topic_focus: Optional specific topic to focus on

    Returns:
        List[MCQuestion]: Document-specific questions
    """
    try:
        import re
        import random

        logger.info(f"Generating {num_questions} document-specific {difficulty} questions")

        if not context or len(context.strip()) < 50:
            logger.warning("Insufficient context for document-specific questions")
            return generate_fallback_questions(context, num_questions, difficulty, topic_focus)

        # Extract meaningful content from the document
        lines = [line.strip() for line in context.split('\n') if line.strip() and len(line.strip()) > 10]

        # Find sentences with technical terms, definitions, or explanations
        meaningful_sentences = []
        for line in lines:
            # Look for lines that contain definitions, explanations, or technical content
            if any(keyword in line.lower() for keyword in ['is', 'are', 'used for', 'allows', 'enables', 'provides', 'implements', 'defines', 'class', 'method', 'function', 'variable', 'syntax', 'example']):
                if len(line) > 20 and len(line) < 200:  # Reasonable length
                    meaningful_sentences.append(line)

        # Extract technical terms and concepts
        technical_terms = set()
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', context)  # Capitalized words
        code_terms = re.findall(r'\b[a-z]+[A-Z][a-zA-Z]*\b', context)  # camelCase
        keywords = re.findall(r'\b(?:class|interface|method|function|variable|array|string|int|boolean|public|private|static|void|return|if|else|for|while|try|catch)\b', context, re.IGNORECASE)

        technical_terms.update(words[:20])  # Limit to avoid too many
        technical_terms.update(code_terms[:10])
        technical_terms.update(keywords[:15])

        # Remove common words
        common_words = {'The', 'This', 'That', 'With', 'From', 'When', 'Where', 'What', 'How', 'Why', 'Which', 'And', 'Or', 'But', 'For', 'In', 'On', 'At', 'To', 'Of', 'By'}
        technical_terms = [term for term in technical_terms if term not in common_words and len(term) > 2]

        questions = []
        used_content = set()

        for i in range(num_questions):
            if meaningful_sentences and technical_terms:
                # Select a sentence that hasn't been used
                available_sentences = [s for s in meaningful_sentences if s not in used_content]
                if not available_sentences:
                    available_sentences = meaningful_sentences

                sentence = random.choice(available_sentences)
                used_content.add(sentence)

                # Extract a key term from the sentence
                sentence_words = re.findall(r'\b[A-Za-z]+\b', sentence)
                key_terms = [word for word in sentence_words if word in technical_terms]

                if key_terms:
                    key_term = random.choice(key_terms)
                    question_text = generate_question_from_content(sentence, key_term, difficulty)
                    options = generate_options_from_content(sentence, key_term, technical_terms, difficulty)

                    question = MCQuestion(
                        question=question_text,
                        options=options,
                        difficulty=difficulty,
                        topic=topic_focus if topic_focus else "Document Content",
                        explanation=f"Based on the document content: {sentence[:100]}...",
                        source_context=sentence
                    )
                    questions.append(question)
                else:
                    # Fallback to generic question for this iteration
                    fallback_q = generate_generic_question_from_sentence(sentence, difficulty, i+1)
                    questions.append(fallback_q)
            else:
                # Generate a basic question from available content
                fallback_q = generate_basic_content_question(context, difficulty, i+1)
                questions.append(fallback_q)

        logger.info(f"Generated {len(questions)} document-specific questions")
        return questions

    except Exception as e:
        logger.error(f"Error generating document-specific questions: {e}")
        return generate_fallback_questions(context, num_questions, difficulty, topic_focus)


def generate_fallback_questions(context: str, num_questions: int = 5,
                               difficulty: str = "medium", topic_focus: str = "") -> List[MCQuestion]:
    """
    Generate dynamic fallback questions that change each time and vary by difficulty.

    Args:
        context: Document content
        num_questions: Number of questions to generate
        difficulty: Difficulty level (easy, medium, hard)
        topic_focus: Optional specific topic to focus on

    Returns:
        List[MCQuestion]: Dynamic fallback questions
    """
    import random

    try:
        # Extract key terms and concepts from context
        words = context.lower().split()

        # Extract document-specific terms (words that appear multiple times)
        word_freq = {}
        for word in words:
            if len(word) > 3 and word.isalpha():  # Filter meaningful words
                word_freq[word] = word_freq.get(word, 0) + 1

        # Get most frequent terms from the document
        document_terms = [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]]

        # Categorized terms for different topics and difficulties (as fallback)
        term_categories = {
            "programming": {
                "easy": ['variable', 'function', 'loop', 'array', 'string', 'number', 'boolean'],
                "medium": ['class', 'method', 'object', 'algorithm', 'structure', 'parameter', 'return'],
                "hard": ['inheritance', 'polymorphism', 'encapsulation', 'abstraction', 'recursion', 'complexity']
            },
            "data_structures": {
                "easy": ['array', 'list', 'stack', 'queue', 'data', 'element', 'index'],
                "medium": ['tree', 'graph', 'hash', 'table', 'linked', 'node', 'pointer'],
                "hard": ['heap', 'trie', 'balanced', 'binary', 'search', 'tree', 'optimization']
            },
            "algorithms": {
                "easy": ['sort', 'search', 'find', 'compare', 'swap', 'iterate', 'count'],
                "medium": ['merge', 'quick', 'binary', 'linear', 'recursive', 'dynamic', 'greedy'],
                "hard": ['dijkstra', 'floyd', 'warshall', 'bellman', 'ford', 'kruskal', 'prim']
            },
            "general": {
                "easy": ['input', 'output', 'print', 'read', 'write', 'file', 'text'],
                "medium": ['database', 'network', 'protocol', 'server', 'client', 'api', 'framework'],
                "hard": ['architecture', 'design', 'pattern', 'scalability', 'performance', 'optimization']
            }
        }

        # Determine which category to use based on topic focus
        if topic_focus:
            topic_lower = topic_focus.lower()
            if any(term in topic_lower for term in ['program', 'code', 'java', 'python', 'c++']):
                category = "programming"
            elif any(term in topic_lower for term in ['data', 'structure', 'array', 'list', 'tree']):
                category = "data_structures"
            elif any(term in topic_lower for term in ['algorithm', 'sort', 'search', 'complexity']):
                category = "algorithms"
            else:
                category = "general"
        else:
            # Auto-detect category from context
            category_scores = {}
            for cat, terms_by_diff in term_categories.items():
                score = 0
                for diff_terms in terms_by_diff.values():
                    score += sum(1 for term in diff_terms if term in words)
                category_scores[cat] = score
            category = max(category_scores, key=category_scores.get)

        # Get terms for the selected difficulty and category
        available_terms = term_categories[category].get(difficulty, term_categories[category]["medium"])

        # Prioritize document-specific terms first
        context_terms = []

        # First, use document-specific terms that appear frequently
        for term in document_terms[:num_questions]:
            if term not in context_terms:
                context_terms.append(term)

        # Then, find predefined terms that actually appear in the context
        for term in available_terms:
            if term in words and term not in context_terms and len(context_terms) < num_questions:
                context_terms.append(term)

        # If no specific terms found, use general terms from context
        if not context_terms:
            for term in term_categories["general"][difficulty]:
                if term in words and len(context_terms) < num_questions:
                    context_terms.append(term)

        # If still no terms, use document terms or fallback to available terms
        if not context_terms:
            context_terms = document_terms[:num_questions] if document_terms else available_terms[:num_questions]

        # Shuffle terms for randomness
        random.shuffle(context_terms)

        # Dynamic question templates based on difficulty
        templates = get_dynamic_templates(difficulty, category)

        questions = []
        used_templates = []

        # Generate questions up to the requested number
        for i in range(num_questions):
            if i < len(context_terms):
                term = context_terms[i].title()
            else:
                # Generate additional terms if needed
                term = f"Concept {i+1}"

            # Select a random template that hasn't been used recently
            available_templates = [t for t in templates if t not in used_templates[-3:]]
            if not available_templates:
                available_templates = templates

            template = random.choice(available_templates)
            used_templates.append(template)

            # Generate dynamic options
            options = generate_dynamic_options(term, difficulty, category, template)

            question = MCQuestion(
                question=template["question"].replace("{term}", term),
                options=options,
                difficulty=difficulty,
                topic=category.replace("_", " ").title(),
                explanation=template["explanation"].replace("{term}", term),
                source_context=context[:200]
            )
            questions.append(question)

        logger.info(f"Generated {len(questions)} dynamic {difficulty} questions for {category}")
        return questions

    except Exception as e:
        logger.error(f"Error generating dynamic fallback questions: {e}")
        return []


def get_dynamic_templates(difficulty: str, category: str) -> List[dict]:
    """Get question templates based on difficulty and category."""

    base_templates = {
        "easy": [
            {
                "question": "What is {term} used for?",
                "explanation": "{term} is a fundamental concept used in programming."
            },
            {
                "question": "Which of the following best describes {term}?",
                "explanation": "{term} is an important element in software development."
            },
            {
                "question": "In programming, {term} is primarily used to:",
                "explanation": "{term} serves a specific purpose in programming contexts."
            }
        ],
        "medium": [
            {
                "question": "What is the main advantage of using {term} in software development?",
                "explanation": "{term} provides specific benefits in software architecture and design."
            },
            {
                "question": "How does {term} contribute to program efficiency?",
                "explanation": "{term} plays a crucial role in optimizing program performance."
            },
            {
                "question": "Which statement about {term} implementation is most accurate?",
                "explanation": "{term} requires careful consideration during implementation."
            }
        ],
        "hard": [
            {
                "question": "What are the computational complexity implications of {term}?",
                "explanation": "{term} has specific time and space complexity characteristics."
            },
            {
                "question": "How does {term} affect system scalability and performance?",
                "explanation": "{term} significantly impacts system architecture and scalability."
            },
            {
                "question": "What are the trade-offs when implementing {term} in large-scale systems?",
                "explanation": "{term} involves complex trade-offs between performance, memory, and maintainability."
            }
        ]
    }

    return base_templates.get(difficulty, base_templates["medium"])


def generate_dynamic_options(term: str, difficulty: str, category: str, template: dict) -> List[MCQOption]:
    """Generate dynamic options based on term, difficulty, and category."""
    import random

    option_pools = {
        "easy": {
            "correct": [
                f"Store and manipulate {term.lower()} data",
                f"Implement {term.lower()} functionality",
                f"Define {term.lower()} behavior",
                f"Handle {term.lower()} operations"
            ],
            "incorrect": [
                "Display user interface elements",
                "Manage network connections",
                "Handle file system operations",
                "Process user authentication",
                "Manage database transactions",
                "Control hardware devices"
            ]
        },
        "medium": {
            "correct": [
                f"Optimize {term.lower()} performance",
                f"Ensure {term.lower()} reliability",
                f"Implement {term.lower()} efficiently",
                f"Maintain {term.lower()} consistency"
            ],
            "incorrect": [
                "Reduce memory overhead significantly",
                "Eliminate all runtime errors",
                "Guarantee thread safety",
                "Prevent security vulnerabilities",
                "Ensure backward compatibility",
                "Minimize compilation time"
            ]
        },
        "hard": {
            "correct": [
                f"Achieve O(log n) complexity for {term.lower()}",
                f"Implement distributed {term.lower()} systems",
                f"Optimize {term.lower()} for concurrent access",
                f"Design fault-tolerant {term.lower()} architecture"
            ],
            "incorrect": [
                "Guarantee constant time complexity",
                "Eliminate all memory leaks",
                "Ensure perfect load balancing",
                "Prevent all race conditions",
                "Achieve 100% cache hit ratio",
                "Eliminate network latency"
            ]
        }
    }

    pool = option_pools.get(difficulty, option_pools["medium"])

    # Select one correct answer
    correct_text = random.choice(pool["correct"])

    # Select three incorrect answers
    incorrect_texts = random.sample(pool["incorrect"], 3)

    # Create options
    options = [MCQOption(correct_text, True)]
    for text in incorrect_texts:
        options.append(MCQOption(text, False))

    # Shuffle options
    random.shuffle(options)

    return options


def generate_question_from_content(sentence: str, key_term: str, difficulty: str) -> str:
    """Generate a question based on document content."""
    templates = {
        "easy": [
            f"What is {key_term} used for according to the document?",
            f"According to the content, {key_term} is:",
            f"The document describes {key_term} as:",
            f"What does the document say about {key_term}?"
        ],
        "medium": [
            f"How does {key_term} function in the context described?",
            f"What is the primary purpose of {key_term} as explained?",
            f"According to the document, what makes {key_term} important?",
            f"How is {key_term} implemented based on the content?"
        ],
        "hard": [
            f"Analyze the role of {key_term} in the overall system described.",
            f"What are the implications of using {key_term} as presented?",
            f"How does {key_term} relate to other concepts in the document?",
            f"What would be the consequence of modifying {key_term}?"
        ]
    }

    import random
    return random.choice(templates.get(difficulty, templates["medium"]))


def generate_options_from_content(sentence: str, key_term: str, technical_terms: list, difficulty: str) -> List[MCQOption]:
    """Generate options based on document content."""
    import random

    # Create a correct answer based on the sentence
    if "is" in sentence.lower():
        parts = sentence.lower().split("is", 1)
        if len(parts) > 1:
            correct_answer = f"It is {parts[1].strip()[:50]}..."
        else:
            correct_answer = f"A key component used in the system"
    else:
        correct_answer = f"An important element described in the document"

    # Generate plausible incorrect answers using other technical terms
    other_terms = [term for term in technical_terms if term != key_term]
    random.shuffle(other_terms)

    incorrect_answers = [
        f"A {other_terms[0] if other_terms else 'generic'} implementation detail",
        f"Used for {other_terms[1] if len(other_terms) > 1 else 'basic'} operations only",
        f"A deprecated feature not recommended for use"
    ]

    # Create options
    options = [MCQOption(correct_answer, True)]
    for answer in incorrect_answers:
        options.append(MCQOption(answer, False))

    # Shuffle options
    random.shuffle(options)
    return options


def generate_generic_question_from_sentence(sentence: str, difficulty: str, question_num: int) -> MCQuestion:
    """Generate a generic question from a sentence."""
    import random

    question_text = f"Based on the document content, which statement is most accurate?"

    options = [
        MCQOption(sentence[:80] + "..." if len(sentence) > 80 else sentence, True),
        MCQOption("This concept is not mentioned in the document", False),
        MCQOption("The document provides contradictory information", False),
        MCQOption("This is a general programming principle", False)
    ]

    random.shuffle(options)

    return MCQuestion(
        question=question_text,
        options=options,
        difficulty=difficulty,
        topic="Document Content",
        explanation=f"This information is directly stated in the document.",
        source_context=sentence
    )


def generate_basic_content_question(context: str, difficulty: str, question_num: int) -> MCQuestion:
    """Generate a basic question from available context."""
    import random

    # Extract first meaningful line
    lines = [line.strip() for line in context.split('\n') if line.strip() and len(line.strip()) > 20]
    content_line = lines[0] if lines else "The document contains technical information"

    question_text = f"According to the document, which of the following is true?"

    options = [
        MCQOption(content_line[:80] + "..." if len(content_line) > 80 else content_line, True),
        MCQOption("The document does not contain this information", False),
        MCQOption("This is contradicted by the document", False),
        MCQOption("This is not relevant to the document topic", False)
    ]

    random.shuffle(options)

    return MCQuestion(
        question=question_text,
        options=options,
        difficulty=difficulty,
        topic="Document Content",
        explanation="This information is found in the document content.",
        source_context=content_line
    )


def create_quiz_session(questions: List[MCQuestion]) -> QuizSession:
    """
    Create a new quiz session.
    
    Args:
        questions: List of questions for the quiz
        
    Returns:
        QuizSession: New quiz session
    """
    session_id = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
    
    return QuizSession(
        session_id=session_id,
        questions=questions,
        user_answers={},
        start_time=datetime.now(),
        total_questions=len(questions)
    )


def calculate_quiz_score(session: QuizSession) -> Tuple[int, int, float]:
    """
    Calculate quiz score.
    
    Args:
        session: Quiz session to score
        
    Returns:
        Tuple[int, int, float]: (correct_answers, total_questions, percentage)
    """
    correct_answers = 0
    total_questions = len(session.questions)
    
    for q_idx, user_answer_idx in session.user_answers.items():
        if q_idx < len(session.questions):
            question = session.questions[q_idx]
            if (user_answer_idx < len(question.options) and 
                question.options[user_answer_idx].is_correct):
                correct_answers += 1
    
    percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    return correct_answers, total_questions, percentage


def get_quiz_feedback(session: QuizSession) -> List[Dict[str, Any]]:
    """
    Generate detailed feedback for quiz answers.
    
    Args:
        session: Completed quiz session
        
    Returns:
        List[Dict]: Feedback for each question
    """
    feedback = []
    
    for q_idx, question in enumerate(session.questions):
        user_answer_idx = session.user_answers.get(q_idx)
        correct_option_idx = next(
            (i for i, opt in enumerate(question.options) if opt.is_correct), 
            None
        )
        
        is_correct = (user_answer_idx is not None and 
                     user_answer_idx == correct_option_idx)
        
        feedback_item = {
            "question_index": q_idx,
            "question": question.question,
            "user_answer": question.options[user_answer_idx].text if user_answer_idx is not None else "Not answered",
            "correct_answer": question.options[correct_option_idx].text if correct_option_idx is not None else "Unknown",
            "is_correct": is_correct,
            "explanation": question.explanation,
            "difficulty": question.difficulty,
            "topic": question.topic
        }
        
        feedback.append(feedback_item)
    
    return feedback
