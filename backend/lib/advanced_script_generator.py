"""
Advanced Script Generation System with Chain-of-Thought Reasoning
Implementation of next-generation script generation techniques
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import re

logger = logging.getLogger(__name__)

class ChainOfThoughtScriptGenerator:
    """
    Advanced script generator using Chain-of-Thought reasoning
    Implements structured reasoning process for higher quality script generation
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.reasoning_steps = [
            "analysis_and_understanding",
            "audience_and_context_mapping", 
            "narrative_architecture_design",
            "engagement_strategy_planning",
            "content_development",
            "quality_validation_and_refinement"
        ]
    
    async def generate_script_with_reasoning(
        self, 
        prompt: str, 
        video_type: str, 
        duration: str,
        enhanced_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate script using Chain-of-Thought reasoning process with template integration
        
        Args:
            prompt: Original user prompt
            video_type: Type of video (educational, marketing, etc.)
            duration: Target duration (short, medium, long)
            enhanced_context: Additional context data including template integration
            
        Returns:
            Dictionary containing script and reasoning process
        """
        try:
            reasoning_chain = {}
            enhanced_context = enhanced_context or {}
            
            # Extract template integration data if available
            template_config = enhanced_context.get("template_config", {})
            segmentation_plan = enhanced_context.get("segmentation_plan", {})
            template_enhanced_prompt = enhanced_context.get("enhanced_prompt", "")
            
            logger.info(f"🧠 Starting CoT generation with template integration: {bool(template_config)}")
            
            # Step 1: Analysis and Understanding (enhanced with template context)
            reasoning_chain["step_1"] = await self._analyze_and_understand(
                prompt, video_type, duration, enhanced_context
            )
            
            # Step 2: Audience and Context Mapping (template-aware)
            reasoning_chain["step_2"] = await self._map_audience_and_context(
                prompt, reasoning_chain["step_1"], enhanced_context
            )
            
            # Step 3: Narrative Architecture Design (template-guided)
            reasoning_chain["step_3"] = await self._design_narrative_architecture(
                prompt, reasoning_chain["step_1"], reasoning_chain["step_2"]
            )
            
            # Step 4: Engagement Strategy Planning (template-optimized)
            reasoning_chain["step_4"] = await self._plan_engagement_strategy(
                reasoning_chain["step_3"], video_type, enhanced_context
            )
            
            # Step 5: Content Development (template-enhanced)
            reasoning_chain["step_5"] = await self._develop_content(
                prompt, reasoning_chain, enhanced_context
            )
            
            # Step 6: Quality Validation and Refinement (template-compliance)
            reasoning_chain["step_6"] = await self._validate_and_refine(
                reasoning_chain["step_5"], reasoning_chain, enhanced_context
            )
            
            final_result = reasoning_chain["step_6"]
            
            return {
                "generated_script": final_result["refined_script"],
                "reasoning_chain": reasoning_chain,
                "final_analysis": final_result["quality_analysis"],
                "generation_metadata": {
                    "method": "chain_of_thought",
                    "steps_completed": len(reasoning_chain),
                    "context_integration": bool(enhanced_context),
                    "template_integration": bool(template_config),
                    "template_id": template_config.get("template_id", "none"),
                    "segmentation_integrated": bool(segmentation_plan),
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in CoT script generation: {str(e)}")
            raise
    
    async def _analyze_and_understand(
        self, 
        prompt: str, 
        video_type: str, 
        duration: str, 
        enhanced_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 1: Deep analysis and understanding of requirements with template integration"""
        
        # Extract template integration context
        template_config = enhanced_context.get("template_config", {})
        template_enhanced_prompt = enhanced_context.get("enhanced_prompt", "")
        segmentation_plan = enhanced_context.get("segmentation_plan", {})
        
        # Build system message with template awareness
        system_message = """You are an expert content analyst specializing in video script requirements analysis with template integration capabilities. 
        Your role is to deeply understand and break down the requirements for script generation while incorporating template-specific guidance.
        
        Analyze each request with systematic precision:
        1. Extract core message and objectives
        2. Identify implicit requirements and constraints  
        3. Determine success criteria and key performance indicators
        4. Assess complexity level and resource requirements
        5. Identify potential challenges and solutions
        6. Integrate template specifications and optimization opportunities
        
        Provide structured, actionable analysis that guides optimal template-enhanced script creation."""
        
        # Enhance system message with template context if available
        if template_config:
            template_name = template_config.get("template_name", "Unknown Template")
            system_message += f"""
            
TEMPLATE INTEGRATION MODE ENABLED:
- Active Template: {template_name}
- Template-guided analysis required
- Consider template specifications in all analysis aspects
- Optimize recommendations for template compatibility"""
        
        analysis_chat = LlmChat(
            api_key=self.api_key,
            session_id=f"cot-analysis-{datetime.utcnow().timestamp()}",
            system_message=system_message
        ).with_model("gemini", "gemini-2.0-flash")
        
        analysis_prompt = f"""
DEEP REQUIREMENT ANALYSIS WITH TEMPLATE INTEGRATION:

USER PROMPT: "{prompt}"
VIDEO TYPE: {video_type}
DURATION: {duration}
CONTEXT AVAILABLE: {bool(enhanced_context)}
TEMPLATE INTEGRATION: {bool(template_config)}

TEMPLATE CONTEXT:
{json.dumps(template_config, indent=2) if template_config else "No template integration available"}

SYSTEMATIC ANALYSIS REQUIRED:

1. CORE MESSAGE EXTRACTION:
   - What is the primary message/objective?
   - What are the secondary messages/sub-objectives?
   - What specific outcomes should this video achieve?

2. IMPLICIT REQUIREMENTS IDENTIFICATION:
   - What unstated expectations exist based on video type?
   - What industry/domain knowledge is required?
   - What tone/style is most appropriate?

3. SUCCESS CRITERIA DEFINITION:
   - How will success be measured for this content?
   - What specific audience actions are desired?
   - What engagement metrics are most important?

4. COMPLEXITY AND RESOURCE ASSESSMENT:
   - What level of expertise is required for this topic?
   - What supporting materials/research might be needed?
   - What production complexity is involved?

5. CHALLENGE IDENTIFICATION:
   - What are potential obstacles in content creation?
   - What audience resistance points might exist?
   - What competitive/market challenges are relevant?

6. OPPORTUNITY RECOGNITION:
   - What unique angles or approaches could be leveraged?
   - What trending topics/themes could be incorporated?
   - What viral potential exists in this concept?

Provide detailed analysis for each category with specific, actionable insights.
"""
        
        analysis_response = await analysis_chat.send_message(UserMessage(text=analysis_prompt))
        
        # Parse structured response
        return {
            "raw_analysis": analysis_response,
            "extracted_insights": self._extract_structured_insights(analysis_response),
            "completion_time": datetime.utcnow().isoformat()
        }
    
    async def _map_audience_and_context(
        self, 
        prompt: str, 
        analysis_step: Dict[str, Any], 
        enhanced_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 2: Map audience characteristics and contextual factors"""
        
        mapping_chat = LlmChat(
            api_key=self.api_key,
            session_id=f"cot-mapping-{datetime.utcnow().timestamp()}",
            system_message="""You are an expert audience psychologist and context strategist specializing in video content optimization.
            
            Your expertise includes:
            - Advanced audience segmentation and persona development
            - Cultural and contextual trend analysis
            - Platform-specific behavior patterns
            - Psychological trigger identification
            - Engagement optimization strategies
            
            Create comprehensive audience and context profiles that directly inform content strategy."""
        ).with_model("gemini", "gemini-2.0-flash")
        
        context_data = enhanced_context.get('audience_psychology', {})
        trend_data = enhanced_context.get('trend_analysis', {})
        platform_data = enhanced_context.get('platform_algorithm', {})
        
        mapping_prompt = f"""
AUDIENCE AND CONTEXT MAPPING:

ANALYSIS INPUT: {analysis_step.get('extracted_insights', {})}
AVAILABLE CONTEXT: {bool(enhanced_context)}

COMPREHENSIVE MAPPING REQUIRED:

1. PRIMARY AUDIENCE PROFILING:
   - Demographics: Age, education, interests, behavior patterns
   - Psychographics: Values, attitudes, motivations, fears
   - Content consumption habits: Preferred formats, timing, platforms
   - Decision-making processes: How they evaluate and act on information

2. SECONDARY AUDIENCE IDENTIFICATION:
   - Who else might be interested in this content?
   - What are their different needs/perspectives?
   - How can content appeal to multiple segments?

3. CONTEXTUAL FACTOR ANALYSIS:
   - Cultural moment: What's happening in society/culture right now?
   - Platform context: How does the target platform influence content?
   - Competitive landscape: What similar content exists?
   - Seasonal/temporal factors: How does timing affect reception?

4. PSYCHOLOGICAL TRIGGER MAPPING:
   - What emotions will resonate most strongly?
   - What cognitive biases can be leveraged ethically?
   - What social proof elements are most compelling?
   - What scarcity/urgency factors apply?

5. ENGAGEMENT PATHWAY DESIGN:
   - How will audience discover this content?
   - What will make them start watching?
   - What will keep them engaged throughout?
   - What will motivate them to share/act?

6. BARRIER AND RESISTANCE ANALYSIS:
   - What might prevent audience engagement?
   - What skepticism or objections need addressing?
   - What competing priorities/distractions exist?
   - How can resistance be overcome?

ENHANCED CONTEXT INTEGRATION:
- Audience Psychology: {context_data}
- Trend Analysis: {trend_data.get('trend_insights', [])}
- Platform Factors: {platform_data.get('priority_factors', [])}

Create detailed, actionable audience and context profiles with specific strategic recommendations.
"""
        
        mapping_response = await mapping_chat.send_message(UserMessage(text=mapping_prompt))
        
        return {
            "raw_mapping": mapping_response,
            "audience_profile": self._extract_audience_profile(mapping_response),
            "context_factors": self._extract_context_factors(mapping_response),
            "completion_time": datetime.utcnow().isoformat()
        }
    
    async def _design_narrative_architecture(
        self, 
        prompt: str, 
        analysis_step: Dict[str, Any], 
        mapping_step: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 3: Design optimal narrative architecture and structure"""
        
        architecture_chat = LlmChat(
            api_key=self.api_key,
            session_id=f"cot-architecture-{datetime.utcnow().timestamp()}",
            system_message="""You are an elite narrative architect and storytelling strategist with expertise in:
            
            - Advanced story structure theories (Hero's Journey, 3-Act Structure, etc.)
            - Video-specific narrative patterns and pacing
            - Emotional arc engineering and tension management
            - Information architecture and cognitive load optimization
            - Platform-specific structure adaptation
            
            Design narrative architectures that maximize engagement, retention, and impact."""
        ).with_model("gemini", "gemini-2.0-flash")
        
        architecture_prompt = f"""
NARRATIVE ARCHITECTURE DESIGN:

ANALYSIS FOUNDATION: {analysis_step.get('extracted_insights', {})}
AUDIENCE MAPPING: {mapping_step.get('audience_profile', {})}

COMPREHENSIVE ARCHITECTURE DESIGN REQUIRED:

1. STRUCTURAL FRAMEWORK SELECTION:
   - What narrative structure best serves the content goals?
   - How should information be sequenced for maximum impact?
   - What pacing rhythm will optimize audience retention?

2. EMOTIONAL ARC ENGINEERING:
   - What emotional journey should the audience experience?
   - Where should emotional peaks and valleys occur?
   - How will emotional state changes drive engagement?

3. INFORMATION ARCHITECTURE:
   - How should complex information be broken down and sequenced?
   - What cognitive load considerations apply?
   - How will key messages be reinforced and remembered?

4. ENGAGEMENT CHECKPOINT DESIGN:
   - Where will critical engagement moments occur?
   - What specific hooks/retention elements are needed?
   - How will attention be recaptured if it wanes?

5. TENSION AND RELEASE PATTERNS:
   - How will curiosity and tension be built and resolved?
   - What questions will drive continued viewing?
   - Where will satisfying payoffs occur?

6. CALL-TO-ACTION INTEGRATION:
   - How will desired actions be naturally integrated?
   - What motivation will be built throughout the narrative?
   - Where will conversion opportunities be optimally placed?

7. PLATFORM-SPECIFIC ADAPTATIONS:
   - How does the platform influence optimal structure?
   - What format-specific elements are required?
   - How will algorithm preferences be accommodated?

Design a detailed narrative architecture with specific structural recommendations, timing suggestions, and engagement strategies.
"""
        
        architecture_response = await architecture_chat.send_message(UserMessage(text=architecture_prompt))
        
        return {
            "raw_architecture": architecture_response,
            "structural_design": self._extract_structural_design(architecture_response),
            "engagement_blueprint": self._extract_engagement_blueprint(architecture_response),
            "completion_time": datetime.utcnow().isoformat()
        }
    
    async def _plan_engagement_strategy(
        self, 
        architecture_step: Dict[str, Any], 
        video_type: str, 
        enhanced_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 4: Plan specific engagement strategies and tactics"""
        
        strategy_chat = LlmChat(
            api_key=self.api_key,
            session_id=f"cot-strategy-{datetime.utcnow().timestamp()}",
            system_message="""You are an expert engagement strategist specializing in video content optimization.
            
            Your expertise covers:
            - Advanced engagement psychology and behavioral triggers
            - Platform-specific engagement tactics and best practices
            - Interactive element design and implementation
            - Viral mechanics and shareability optimization
            - Conversion strategy and call-to-action optimization
            
            Create comprehensive engagement strategies that maximize viewer interaction and desired outcomes."""
        ).with_model("gemini", "gemini-2.0-flash")
        
        performance_data = enhanced_context.get('performance_history', {})
        platform_data = enhanced_context.get('platform_algorithm', {})
        
        strategy_prompt = f"""
ENGAGEMENT STRATEGY PLANNING:

NARRATIVE ARCHITECTURE: {architecture_step.get('structural_design', {})}
VIDEO TYPE: {video_type}
PERFORMANCE CONTEXT: {performance_data.get('optimization_opportunities', [])}

COMPREHENSIVE STRATEGY DEVELOPMENT REQUIRED:

1. HOOK STRATEGY DESIGN:
   - What specific opening techniques will capture attention?
   - How will the first 3-5 seconds be optimized?
   - What pattern interrupts and curiosity gaps will be used?

2. RETENTION STRATEGY IMPLEMENTATION:
   - What specific elements will maintain attention throughout?
   - How will retention be recovered if viewer attention drops?
   - What surprise elements and reveals will be strategically placed?

3. INTERACTION STRATEGY PLANNING:
   - What questions will encourage mental/physical engagement?
   - How will viewers be prompted to participate actively?
   - What interactive elements are appropriate for the platform?

4. EMOTIONAL ENGAGEMENT TACTICS:
   - What specific emotional triggers will be activated?
   - How will emotional intensity be modulated for optimal impact?
   - What personal connection points will be established?

5. SOCIAL ENGAGEMENT OPTIMIZATION:
   - What elements will encourage sharing and discussion?
   - How will social proof be integrated naturally?
   - What conversation starters will be embedded?

6. CONVERSION STRATEGY EXECUTION:
   - How will desired actions be motivated throughout?
   - What specific call-to-action approaches will be used?
   - How will conversion barriers be addressed and overcome?

7. PLATFORM-SPECIFIC TACTICS:
   - What platform-specific engagement features will be leveraged?
   - How will algorithm preferences be satisfied?
   - What format-specific best practices will be implemented?

PLATFORM OPTIMIZATION DATA:
- Priority Factors: {platform_data.get('priority_factors', [])}
- Engagement Weights: {platform_data.get('engagement_weights', {})}
- Trending Formats: {platform_data.get('trending_formats', [])}

Create a detailed engagement strategy with specific tactics, timing, and implementation guidance.
"""
        
        strategy_response = await strategy_chat.send_message(UserMessage(text=strategy_prompt))
        
        return {
            "raw_strategy": strategy_response,
            "engagement_tactics": self._extract_engagement_tactics(strategy_response),
            "platform_optimizations": self._extract_platform_optimizations(strategy_response),
            "completion_time": datetime.utcnow().isoformat()
        }
    
    async def _develop_content(
        self, 
        prompt: str, 
        reasoning_chain: Dict[str, Any], 
        enhanced_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 5: Develop actual script content based on reasoning chain with template enhancement"""
        
        # Extract template context
        template_config = enhanced_context.get("template_config", {})
        enhanced_prompt = enhanced_context.get("enhanced_prompt", "")
        segmentation_plan = enhanced_context.get("segmentation_plan", {})
        
        # Build template-enhanced system message
        system_message = """You are an elite script writer with the ability to synthesize complex strategic insights into compelling, production-ready video scripts.
        
        Your capabilities include:
        - Translating strategic frameworks into engaging narrative content
        - Optimizing language for maximum emotional and psychological impact
        - Integrating complex requirements seamlessly into natural-flowing content
        - Creating visually-rich, production-ready script specifications
        - Balancing entertainment value with informational content
        - Template-enhanced script generation with professional optimization
        
        Generate scripts that perfectly execute the strategic vision while remaining engaging and natural."""
        
        # Add template-specific guidance if available
        if template_config and enhanced_prompt:
            template_name = template_config.get("template_name", "Unknown Template")
            system_message += f"""

TEMPLATE INTEGRATION ACTIVE:
- Active Template: {template_name}
- Use the enhanced prompt specifications as your primary guide
- Incorporate template-specific expertise and structure requirements
- Ensure output meets template quality and formatting standards"""
        
        content_chat = LlmChat(
            api_key=self.api_key,
            session_id=f"cot-content-{datetime.utcnow().timestamp()}",
            system_message=system_message
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Synthesize all reasoning chain insights
        analysis_insights = reasoning_chain["step_1"].get("extracted_insights", {})
        audience_profile = reasoning_chain["step_2"].get("audience_profile", {})
        structural_design = reasoning_chain["step_3"].get("structural_design", {})
        engagement_tactics = reasoning_chain["step_4"].get("engagement_tactics", {})
        
        content_prompt = f"""
TEMPLATE-ENHANCED SCRIPT CONTENT DEVELOPMENT:

ORIGINAL PROMPT: "{prompt}"

STRATEGIC SYNTHESIS:
- Core Analysis: {analysis_insights}
- Audience Profile: {audience_profile}
- Narrative Architecture: {structural_design}
- Engagement Strategy: {engagement_tactics}

TEMPLATE INTEGRATION CONTEXT:
{json.dumps(template_config, indent=2) if template_config else "No template integration"}

ENHANCED PROMPT SPECIFICATIONS:
{enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt}

SEGMENTATION REQUIREMENTS:
{json.dumps(segmentation_plan, indent=2) if segmentation_plan else "No segmentation requirements"}

SCRIPT DEVELOPMENT REQUIREMENTS:

1. IMPLEMENT STRATEGIC ARCHITECTURE:
   - Execute the designed narrative structure precisely
   - Integrate all identified engagement tactics naturally
   - Maintain optimal pacing and emotional arc
   - Include all specified retention and interaction elements
   - Follow template-specific structural guidelines

2. TEMPLATE COMPLIANCE:
   - Adhere to enhanced prompt specifications
   - Maintain template-defined expertise level and tone
   - Implement template-specific segment requirements
   - Follow template quality and formatting standards

3. AUDIENCE-OPTIMIZED LANGUAGE:
   - Use language patterns that resonate with target audience
   - Incorporate appropriate tone, complexity, and style
   - Address identified concerns and motivations directly
   - Include relevant cultural references and context

3. PRODUCTION-READY SPECIFICATIONS:
   - Include detailed visual and audio direction
   - Specify timing, pacing, and transition elements
   - Provide clear guidance for video production
   - Integrate platform-specific optimization requirements

4. ENGAGEMENT ELEMENT INTEGRATION:
   - Seamlessly incorporate planned hooks and retention tactics
   - Include interactive elements and participation cues
   - Embed social proof and credibility indicators
   - Integrate call-to-action elements naturally

5. QUALITY AND POLISH:
   - Ensure natural flow and readability
   - Optimize for both spoken delivery and visual impact
   - Maintain consistency with brand/style requirements
   - Include contingencies for different production scenarios

ENHANCED CONTEXT INTEGRATION:
{json.dumps(enhanced_context, indent=2) if enhanced_context else "No additional context available"}

Generate a comprehensive, production-ready script that flawlessly executes the strategic vision while remaining engaging, natural, and highly effective.
"""
        
        content_response = await content_chat.send_message(UserMessage(text=content_prompt))
        
        return {
            "raw_content": content_response,
            "script_sections": self._parse_script_sections(content_response),
            "production_notes": self._extract_production_notes(content_response),
            "completion_time": datetime.utcnow().isoformat()
        }
    
    async def _validate_and_refine(
        self, 
        content_step: Dict[str, Any], 
        reasoning_chain: Dict[str, Any], 
        enhanced_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 6: Validate script quality and refine if necessary"""
        
        validation_chat = LlmChat(
            api_key=self.api_key,
            session_id=f"cot-validation-{datetime.utcnow().timestamp()}",
            system_message="""You are an expert script quality analyst and optimizer with the ability to:
            
            - Evaluate script effectiveness against strategic objectives
            - Identify gaps, weaknesses, and improvement opportunities
            - Optimize content for maximum impact and engagement
            - Ensure all requirements are met comprehensively
            - Provide specific, actionable refinement recommendations
            
            Your role is to ensure the final script achieves maximum possible effectiveness."""
        ).with_model("gemini", "gemini-2.0-flash")
        
        original_script = content_step.get("raw_content", "")
        
        validation_prompt = f"""
SCRIPT QUALITY VALIDATION AND REFINEMENT:

GENERATED SCRIPT:
{original_script}

STRATEGIC REQUIREMENTS VALIDATION:
- Original Analysis: {reasoning_chain["step_1"].get("extracted_insights", {})}
- Audience Requirements: {reasoning_chain["step_2"].get("audience_profile", {})}
- Structural Requirements: {reasoning_chain["step_3"].get("structural_design", {})}
- Engagement Requirements: {reasoning_chain["step_4"].get("engagement_tactics", {})}

COMPREHENSIVE VALIDATION CHECKLIST:

1. STRATEGIC ALIGNMENT ASSESSMENT:
   - Does the script achieve the identified core objectives?
   - Are all audience needs and preferences addressed?
   - Is the narrative architecture properly implemented?
   - Are engagement tactics effectively integrated?

2. QUALITY METRICS EVALUATION:
   - Hook strength and attention-grabbing effectiveness
   - Information density and cognitive load optimization
   - Emotional arc strength and impact potential
   - Retention element placement and effectiveness
   - Call-to-action clarity and motivation

3. PRODUCTION READINESS CHECK:
   - Visual and audio direction completeness
   - Timing and pacing specification accuracy
   - Platform optimization requirement fulfillment
   - Technical production feasibility

4. IMPROVEMENT OPPORTUNITY IDENTIFICATION:
   - What specific elements could be strengthened?
   - Where are gaps in strategic implementation?
   - What refinements would increase effectiveness?
   - How can engagement be further optimized?

5. FINAL OPTIMIZATION:
   If improvements are needed, provide a refined version that addresses all identified gaps and optimization opportunities.

Provide detailed validation analysis and a final, optimized script version if refinements are beneficial.
"""
        
        validation_response = await validation_chat.send_message(UserMessage(text=validation_prompt))
        
        # Extract refined script if provided
        refined_script = self._extract_refined_script(validation_response, original_script)
        
        return {
            "raw_validation": validation_response,
            "quality_analysis": self._extract_quality_analysis(validation_response),
            "refined_script": refined_script,
            "validation_score": self._calculate_validation_score(validation_response),
            "completion_time": datetime.utcnow().isoformat()
        }
    
    # Helper methods for parsing and structuring responses
    
    def _extract_structured_insights(self, analysis_response: str) -> Dict[str, Any]:
        """Extract structured insights from analysis response"""
        try:
            # Simple pattern matching for key insights
            insights = {}
            
            # Extract core message
            if "primary message" in analysis_response.lower() or "core message" in analysis_response.lower():
                insights["core_message"] = "Identified and extracted"
            
            # Extract complexity level
            if "complex" in analysis_response.lower():
                insights["complexity"] = "High"
            elif "simple" in analysis_response.lower():
                insights["complexity"] = "Low" 
            else:
                insights["complexity"] = "Medium"
            
            # Extract success indicators
            insights["success_criteria"] = "Analyzed" if "success" in analysis_response.lower() else "Not specified"
            
            return insights
            
        except Exception as e:
            logger.warning(f"Error extracting insights: {str(e)}")
            return {"extraction_error": str(e)}
    
    def _extract_audience_profile(self, mapping_response: str) -> Dict[str, Any]:
        """Extract audience profile from mapping response"""
        try:
            profile = {}
            
            # Basic audience characteristics extraction
            if "demographic" in mapping_response.lower():
                profile["demographics"] = "Analyzed"
            if "psychographic" in mapping_response.lower():
                profile["psychographics"] = "Analyzed"
            if "behavior" in mapping_response.lower():
                profile["behavior_patterns"] = "Analyzed"
            
            return profile
            
        except Exception as e:
            logger.warning(f"Error extracting audience profile: {str(e)}")
            return {"extraction_error": str(e)}
    
    def _extract_context_factors(self, mapping_response: str) -> Dict[str, Any]:
        """Extract context factors from mapping response"""
        try:
            factors = {}
            
            # Context factor identification
            if "cultural" in mapping_response.lower():
                factors["cultural_context"] = "Analyzed"
            if "platform" in mapping_response.lower():
                factors["platform_context"] = "Analyzed"
            if "competitive" in mapping_response.lower():
                factors["competitive_context"] = "Analyzed"
            
            return factors
            
        except Exception as e:
            logger.warning(f"Error extracting context factors: {str(e)}")
            return {"extraction_error": str(e)}
    
    def _extract_structural_design(self, architecture_response: str) -> Dict[str, Any]:
        """Extract structural design from architecture response"""
        try:
            design = {}
            
            # Structure identification
            if "hook" in architecture_response.lower():
                design["hook_strategy"] = "Designed"
            if "narrative" in architecture_response.lower():
                design["narrative_structure"] = "Designed"
            if "emotional arc" in architecture_response.lower():
                design["emotional_arc"] = "Designed"
            
            return design
            
        except Exception as e:
            logger.warning(f"Error extracting structural design: {str(e)}")
            return {"extraction_error": str(e)}
    
    def _extract_engagement_blueprint(self, architecture_response: str) -> Dict[str, Any]:
        """Extract engagement blueprint from architecture response"""
        try:
            blueprint = {}
            
            # Engagement element identification
            if "engagement" in architecture_response.lower():
                blueprint["engagement_elements"] = "Planned"
            if "retention" in architecture_response.lower():
                blueprint["retention_strategy"] = "Planned"
            if "interaction" in architecture_response.lower():
                blueprint["interaction_points"] = "Planned"
            
            return blueprint
            
        except Exception as e:
            logger.warning(f"Error extracting engagement blueprint: {str(e)}")
            return {"extraction_error": str(e)}
    
    def _extract_engagement_tactics(self, strategy_response: str) -> Dict[str, Any]:
        """Extract engagement tactics from strategy response"""
        try:
            tactics = {}
            
            # Tactic identification
            if "hook" in strategy_response.lower():
                tactics["hook_tactics"] = "Specified"
            if "retention" in strategy_response.lower():
                tactics["retention_tactics"] = "Specified"
            if "interaction" in strategy_response.lower():
                tactics["interaction_tactics"] = "Specified"
            
            return tactics
            
        except Exception as e:
            logger.warning(f"Error extracting engagement tactics: {str(e)}")
            return {"extraction_error": str(e)}
    
    def _extract_platform_optimizations(self, strategy_response: str) -> Dict[str, Any]:
        """Extract platform optimizations from strategy response"""
        try:
            optimizations = {}
            
            # Platform optimization identification
            if "algorithm" in strategy_response.lower():
                optimizations["algorithm_optimization"] = "Planned"
            if "format" in strategy_response.lower():
                optimizations["format_optimization"] = "Planned"
            if "engagement" in strategy_response.lower():
                optimizations["engagement_optimization"] = "Planned"
            
            return optimizations
            
        except Exception as e:
            logger.warning(f"Error extracting platform optimizations: {str(e)}")
            return {"extraction_error": str(e)}
    
    def _parse_script_sections(self, content_response: str) -> Dict[str, Any]:
        """Parse script into sections"""
        try:
            sections = {}
            
            # Basic section identification
            if content_response:
                sections["full_script"] = content_response
                sections["word_count"] = len(content_response.split())
                sections["character_count"] = len(content_response)
            
            return sections
            
        except Exception as e:
            logger.warning(f"Error parsing script sections: {str(e)}")
            return {"parsing_error": str(e)}
    
    def _extract_production_notes(self, content_response: str) -> Dict[str, Any]:
        """Extract production notes from content response"""
        try:
            notes = {}
            
            # Production element identification
            if "[" in content_response and "]" in content_response:
                notes["visual_directions"] = "Included"
            if "(" in content_response and ")" in content_response:
                notes["audio_directions"] = "Included"
            
            return notes
            
        except Exception as e:
            logger.warning(f"Error extracting production notes: {str(e)}")
            return {"extraction_error": str(e)}
    
    def _extract_quality_analysis(self, validation_response: str) -> Dict[str, Any]:
        """Extract quality analysis from validation response"""
        try:
            analysis = {}
            
            # Quality metric identification
            if "effective" in validation_response.lower():
                analysis["effectiveness"] = "High"
            elif "ineffective" in validation_response.lower():
                analysis["effectiveness"] = "Low"
            else:
                analysis["effectiveness"] = "Medium"
            
            if "improvement" in validation_response.lower():
                analysis["improvement_needed"] = "Yes"
            else:
                analysis["improvement_needed"] = "No"
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Error extracting quality analysis: {str(e)}")
            return {"extraction_error": str(e)}
    
    def _extract_refined_script(self, validation_response: str, original_script: str) -> str:
        """Extract refined script from validation response"""
        try:
            # Look for improved version in validation response
            # If specific refinements are provided, use them; otherwise use original
            
            # Simple check for refined version
            if "refined" in validation_response.lower() or "improved" in validation_response.lower():
                # In a real implementation, this would parse the refined script more intelligently
                # For now, we'll use the validation response if it contains substantial content
                if len(validation_response) > len(original_script) * 0.5:
                    return validation_response
            
            return original_script
            
        except Exception as e:
            logger.warning(f"Error extracting refined script: {str(e)}")
            return original_script
    
    def _calculate_validation_score(self, validation_response: str) -> float:
        """Calculate validation score from response"""
        try:
            score = 7.0  # Base score
            
            # Adjust based on validation indicators
            if "excellent" in validation_response.lower():
                score += 2.0
            elif "good" in validation_response.lower():
                score += 1.0
            elif "poor" in validation_response.lower():
                score -= 2.0
            
            if "improvement" in validation_response.lower():
                score -= 0.5
            
            return min(10.0, max(0.0, score))
            
        except Exception as e:
            logger.warning(f"Error calculating validation score: {str(e)}")
            return 5.0