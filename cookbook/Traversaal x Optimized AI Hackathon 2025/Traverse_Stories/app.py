import streamlit as st
import os

# Now do the rest of the imports
import sys
import asyncio
from tavily import TavilyClient
from dotenv import load_dotenv
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context
)
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage, MessageRole
from agentpro import ReactAgent
from agentpro.tools import Tool
from openai import OpenAI as oai
import requests
import base64
import json
from pydantic import BaseModel

load_dotenv()

# Function to download image from a URL
def download_image(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print('illustration done')
    else:
        print('pass')

# Function to load and display audio
def get_audio_player(audio_path):
    if os.path.exists(audio_path):
        audio_file = open(audio_path, 'rb')
        audio_bytes = audio_file.read()
        audio_file.close()
        return audio_bytes
    return None

# Function to read markdown files
def read_markdown_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

# Custom AgentPro Tools
class TeaserTool(Tool):
    name: str = "Teaser Writer Tool"
    description: str = "Creates a catchy 2-sentence teaser for a story to post on social media"
    action_type: str = "teaser_writer_tool"
    input_format: str = "Story"

    def run(self, story: str) -> str:
        llm = OpenAI(model='gpt-4o-mini')
        teaser = llm.complete(
            f"""you are a veteran teaser writer for short stories. here is a short story: {story}. 
            read it carefully and write a very catchy hooking 2-sentence teaser for it to post on social media. write in md syntax"""
        )
        content = str(teaser).strip() 
        
        return content

class IllustrationTool(Tool):
    name: str = "Illustration Tool"
    description: str = "Creates a prompt for an illustration using DALL-E"
    action_type: str = "illustration_tool"
    input_format: str = "Story"

    def run(self, story: str) -> str:
        try:
            llm = OpenAI(model='gpt-4o-mini')
            prompt = llm.complete(
                f"""you are a veteran illustration artist for short stories. here is a short story: {story}.
                think of concept for an anime style illustration for this story and write a prompt for DALL-E-3 to draw it. your prompt:"""
            )
            prompt_content = str(prompt).split("prompt:")[-1].strip()
            return prompt_content
          
        except Exception as e:
            print(f"Error creating illustration: {e}")
            return None

class AudiobookTool(Tool):
    name: str = "Audiobook Tool"
    description: str = "Creates an audio narration of the story"
    action_type: str = "audiobook_tool"
    input_format: str = "Story"

    def run(self, story: str) -> str:
        try:
            client = oai()
            audio_path = "publication/story_audio.mp3"
            
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice="onyx",
                input=story
            )
            
            # Write audio content directly
            with open(audio_path, 'wb') as audio_file:
                for chunk in response.iter_bytes():
                    audio_file.write(chunk)
            
            print(f"Audio saved to {audio_path}")
            return audio_path
        except Exception as e:
            print(f"Error creating audio: {e}")
            return None

# Add TranslationTool class
class TranslationTool(Tool):
    name: str = "Translation Tool"
    description: str = "Create a translation of the story into Japanese"
    action_type: str = "translation_tool"
    input_format: str = "Story"

    def run(self, story: str) -> str:
        llm = OpenAI(model='gpt-4o-mini')
        translation = llm.complete(
            f"""you are a veteran English to Japanese translator for short stories. here is a short story: {story}.
            read it carefully and then translate it into Japanese, be thoughtful about the nuances of the languages. write in md syntax. your translation:"""
        )
          # Extract just the translation
        with open('publication/translation.md', 'w', encoding='utf-8') as f:
            f.write(translation)
        return story

# Event classes remain the same
class SubtopicPackage(Event):
    subtopic: str

class SubtopicSourceMaterialPackage(Event):
    subtopic_source_materials: str
    
class SourceMaterialPackage(Event):
    source_materials: str

class DraftStoryPackage(Event):
    draft_story: str

class EditorCommentaryPackage(Event):
    editor_commentary: str
    
class FinalStoryPackage(Event):
    final_story: str

class ContentSubtopics(BaseModel):
    subtopic_one: str
    subtopic_two: str
    subtopic_three: str

class StoryPublicationFlow(Workflow):
    @step
    async def research_source_materials(self, ctx: Context, ev: StartEvent) -> SubtopicPackage: 
        topic = ev.query
        print(f'🔍 Researching main topic: {topic}')
        await ctx.set('topic', topic)

        tavily_client = TavilyClient()
        response = tavily_client.search(topic)
        source_materials = '\n'.join(result['content'] for result in response['results'])

        print('📚 Analyzing source materials to generate subtopics...')
        llm = OpenAI(model='gpt-4o-mini')
        sllm = llm.as_structured_llm(output_cls=ContentSubtopics)
        input_msg = ChatMessage.from_str(f"Generate a list of 3 searchable subtopics to be passed into a search engine for deeper research based on these info about the {topic}: {source_materials}")
        response = sllm.chat([input_msg])
        
        subtopics = json.loads(response.message.content)
        print(f'🎯 Generated subtopics: {", ".join(subtopics.values())}')
        
        await ctx.set('subtopics', subtopics)
        await ctx.set('num_subtopics', len(subtopics))
        for subtopic in subtopics.values():
            ctx.send_event(SubtopicPackage(subtopic = subtopic))
    
    @step(num_workers=3)
    async def research_subtopics(self, ctx: Context, ev: SubtopicPackage) -> SubtopicSourceMaterialPackage:
        subtopic = ev.subtopic
        print(f'🔍 Researching subtopic: {subtopic}')
        tavily_client = TavilyClient()
        response = tavily_client.search(subtopic)
        subtopic_materials = '\n'.join(result['content'] for result in response['results'])
        return SubtopicSourceMaterialPackage(subtopic_source_materials = subtopic_materials)
    
    @step
    async def combine_research_subtopics(self, ctx: Context, ev: SubtopicSourceMaterialPackage) -> SourceMaterialPackage:
        print('📋 Combining research from all subtopics...')
        num_packages = await ctx.get('num_subtopics')
        
        source_materials = ctx.collect_events(ev, [SubtopicSourceMaterialPackage] * num_packages)
        if source_materials is None:
            return None
        
        source_materials = '\n'.join(result.subtopic_source_materials for result in source_materials)
        print('✅ Research compilation complete')
        return SourceMaterialPackage(source_materials = source_materials)

    @step
    async def write_story(self, ctx: Context, ev: SourceMaterialPackage| EditorCommentaryPackage) -> DraftStoryPackage| FinalStoryPackage:
        if isinstance(ev, SourceMaterialPackage):
            print('✍️ Writing initial draft of the story...')
            topic = await ctx.get('topic')
            source_materials = ev.source_materials
            llm = OpenAI(model='gpt-4o-mini', max_tokens=4096)
            response = await llm.acomplete(f'''you are a world famous fiction writer of scifi short stories. 
                                        you are tasked with writing a super short story about {topic}.
                                        these are some source materials for you to choose from and use to write the story: {source_materials}''')
            await ctx.set('draft_story', str(response))
            print('📝 First draft complete')
            return DraftStoryPackage(draft_story = str(response))
        
        else:
            print('✍️ Refining the story based on editor feedback...')
            topic = await ctx.get('topic')
            editor_commentary = ev.editor_commentary
            draft_story = await ctx.get('draft_story')
            llm = OpenAI(model='gpt-4o-mini')
            response = await llm.acomplete(f'''you are a world famous fiction writer of scifi short stories. 
                                        you are tasked with writing a super short story about {topic}.
                                        
                                        here is a draft of the story you wrote: {draft_story}
                                        here is the commentary from the editor: {editor_commentary}
                                        refine it to make it more engaging and interesting. your refined story, only put the story, NO other commentary:''')
            with open('publication/final_story.md', 'w', encoding='utf-8') as f:
                f.write(str(response))
            print('✨ Final story complete')
            return FinalStoryPackage(final_story = str(response))
    
    @step
    async def refine_draft_story(self, ctx: Context, ev: DraftStoryPackage) -> EditorCommentaryPackage:
        print('📋 Editor reviewing the draft...')
        topic = await ctx.get('topic')
        draft_story = ev.draft_story
        
        llm = OpenAI(model='gpt-4o-mini')
        response = await llm.acomplete(f'''you are a veteran publishing house editor for short stories. here is a short story about {topic}: {draft_story}. 
                                           read it carefully and suggest ideas for improvement. write in md syntax''')
        print('✅ Editor feedback ready')
        return EditorCommentaryPackage(editor_commentary = str(response))
        
    @step
    async def generate_content(self, ctx: Context, ev: FinalStoryPackage) -> StopEvent:
        print('🎨 Starting content generation phase...')
        final_story = ev.final_story
        
        # Generate teaser
        print('📢 Creating social media teaser...')
        teaser_agent = ReactAgent(model = os.getenv('OPENAI_API_KEY', None), tools=[TeaserTool()])
        teaser = teaser_agent.run(f"Create a teaser for this story: {final_story}").final_answer
        with open('publication/teaser.md', 'w', encoding='utf-8') as f:
            f.write(teaser)
        print('✅ Teaser created')
        
        # Generate translation
        print('📝 Translating story to Japanese...')
        llm = OpenAI(model='gpt-4o-mini')

        
        translation = llm.complete(
            f"""you are a veteran English to Japanese translator for short stories. here is a short story: {final_story}.
            read it carefully and then translate it into Japanese, be thoughtful about the nuances of the languages. 
            write in md syntax. start immediately with your Japanese translation:"""
        )
        
        with open('publication/translation.md', 'w', encoding='utf-8') as f:
            f.write(translation.text)
        print('✅ Translation complete')
        
        # Generate illustration
        print('🎨 Generating story illustration...')
        illustration_agent = ReactAgent(model = os.getenv('OPENAI_API_KEY', None), tools=[IllustrationTool()])
        illustration_prompt = illustration_agent.run(f"Create an illustration for this story: {final_story}").final_answer

        client = oai()
        response = client.images.generate(
            model="dall-e-3",
            prompt=illustration_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        
        illustration_path = "publication/story_illustration.jpg"
        
        # Download image using requests
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            with open(illustration_path, 'wb') as f:
                f.write(img_response.content)
            print(f"Illustration saved to {illustration_path}")
            
        else:
            print(f"Failed to download image: {img_response.status_code}")
            
        # Generate audio
        print('🎧 Creating audio narration...')
        client = oai()
        audio_path = "publication/story_audio.mp3"
        
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            input=final_story
        )
        
        # Write audio content directly
        with open(audio_path, 'wb') as audio_file:
            for chunk in response.iter_bytes():
                audio_file.write(chunk)
        
        print(f"Audio saved to {audio_path}")
        # Verify audio was created
        if not os.path.exists('publication/story_audio.mp3'):
            print('⚠️ Warning: Audio file not created')
        else:
            print('✅ Audio narration created')
        
        print('✨ All content generation complete!')
        
        
        return StopEvent(result='all done')

async def generate_story(topic):
    # create publication directory if it doesn't exist
    os.makedirs('publication', exist_ok=True)
    
    w = StoryPublicationFlow(timeout=10000, verbose=False)
    return await w.run(query=topic)

def main():
    st.title("Traverse Story - The AI Publishing House 🔖")
    
    # Input section
    topic = st.text_input("What topic do you want to write a short story about?")
    
    if st.button("Generate Story"):
        # Create a status container
        status_area = st.empty()
        progress_area = st.empty()
        
        with st.spinner("Generating your story and related content..."):
            # Create progress placeholder
            progress_text = ""
            
            def update_status(message):
                nonlocal progress_text
                # Only display messages that start with emojis (our progress indicators)
                if any(emoji in message for emoji in ['🔍', '📚', '🎯', '✍️', '📝', '✅', '📋', '🎨', '📢', '🎧', '✨', '⚠️']):
                    progress_text += f"{message}\n"
                    status_area.code(progress_text)
            
            # Monkey patch print to update status
            original_print = print
            def custom_print(*args, **kwargs):
                message = " ".join(map(str, args))
                update_status(message)
                original_print(*args, **kwargs)
            
            import builtins
            builtins.print = custom_print
            
            try:
                # Run the async workflow
                result = asyncio.run(generate_story(topic))
                
                # Display the results in tabs
                tab1, tab2, tab3, tab4 = st.tabs(["Story", "Teaser", "Translation", "Media"])
                
                with tab1:
                    st.header("Generated Story")
                    story_content = read_markdown_file('publication/final_story.md')
                    if story_content:
                        st.markdown(story_content)
                
                with tab2:
                    st.header("Story Teaser")
                    teaser_content = read_markdown_file('publication/teaser.md')
                    if teaser_content:
                        st.markdown(teaser_content)
                
                with tab3:
                    st.header("Translation")
                    translation_content = read_markdown_file('publication/translation.md')
                    if translation_content:
                        st.markdown(translation_content)
                
                with tab4:
                    st.header("Story Illustration")
                    if os.path.exists('publication/story_illustration.jpg'):
                        st.image('publication/story_illustration.jpg')
                    
                    st.header("Audio Narration")
                    audio_bytes = get_audio_player('publication/story_audio.mp3')
                    if audio_bytes:
                        st.audio(audio_bytes, format='audio/mp3')
            
            finally:
                # Restore original print function
                builtins.print = original_print

if __name__ == "__main__":
    main() 