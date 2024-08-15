from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.services.ai_service import AIService
import logging
import json

router = APIRouter()

@router.get("/stream")
async def stream_message(request: Request, ai_service: AIService = Depends(AIService)):
    logging.info("Received stream request")
    try:
        message = request.query_params.get('message')
        context_str = request.query_params.get('context', '[]')
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        context = json.loads(context_str)
        
        logging.info(f'Streaming message: {message}')
        logging.info(f'Context: {context}')

        for msg in context:
            await ai_service.add_message_to_thread(msg['content'], msg['role'])
        
        await ai_service.add_message_to_thread(message)
        
        return StreamingResponse(ai_service.run_assistant_stream(), media_type="text/event-stream")
    except json.JSONDecodeError:
        logging.error("Invalid JSON in context parameter")
        raise HTTPException(status_code=400, detail="Invalid context format")
    except Exception as e:
        logging.error(f"Error in stream_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))