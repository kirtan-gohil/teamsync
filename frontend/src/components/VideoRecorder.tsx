import React, { useRef, useEffect, useState } from 'react';

interface VideoRecorderProps {
  onVideoData?: (videoBlob: Blob) => void;
  onEyeTrackingData?: (data: any) => void;
  isRecording: boolean;
  className?: string;
}

const VideoRecorder: React.FC<VideoRecorderProps> = ({ 
  onVideoData, 
  onEyeTrackingData, 
  isRecording, 
  className = "" 
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [eyeTrackingActive, setEyeTrackingActive] = useState(false);

  useEffect(() => {
    if (isRecording && !stream) {
      startCamera();
    } else if (!isRecording && stream) {
      stopCamera();
    }
  }, [isRecording]);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: 640, 
          height: 480,
          facingMode: 'user'
        },
        audio: true
      });
      
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }

      // Start video recording
      const mediaRecorder = new MediaRecorder(mediaStream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const videoBlob = new Blob(chunksRef.current, { type: 'video/webm' });
        if (onVideoData) {
          onVideoData(videoBlob);
        }
      };

      mediaRecorder.start();
      setEyeTrackingActive(true);
      startEyeTracking();

    } catch (error) {
      console.error('Error accessing camera:', error);
    }
  };

  const stopCamera = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    
    setEyeTrackingActive(false);
  };

  const startEyeTracking = () => {
    let eyeMovements = 0;
    let distractionCount = 0;
    let attentionScore = 100;
    let consecutiveCenterGaze = 0;
    
    // Simulate more realistic eye tracking data
    const interval = setInterval(() => {
      if (eyeTrackingActive && onEyeTrackingData) {
        // More realistic eye movement patterns
        const isLookingAway = Math.random() < 0.15; // 15% chance of looking away
        const gazeDirection = isLookingAway ? 
          ['left', 'right', 'up', 'down'][Math.floor(Math.random() * 4)] : 
          'center';
        
        // Track consecutive center gaze for attention
        if (gazeDirection === 'center') {
          consecutiveCenterGaze++;
        } else {
          consecutiveCenterGaze = 0;
          distractionCount++;
        }
        
        // Calculate attention score based on focus
        if (consecutiveCenterGaze > 5) {
          attentionScore = Math.min(100, attentionScore + 2); // Reward focus
        } else if (isLookingAway) {
          attentionScore = Math.max(20, attentionScore - 5); // Penalize distraction
        }
        
        // Occasional eye movements even when focused
        if (Math.random() < 0.3) {
          eyeMovements++;
        }
        
        const eyeData = {
          eyeMovements,
          gazeDirection,
          attentionScore: Math.round(attentionScore),
          distractionCount
        };
        
        onEyeTrackingData(eyeData);
      }
    }, 1000);

    return () => clearInterval(interval);
  };

  useEffect(() => {
    if (eyeTrackingActive) {
      const cleanup = startEyeTracking();
      return cleanup;
    }
  }, [eyeTrackingActive]);

  return (
    <div className={`relative ${className}`}>
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full h-64 object-cover rounded-lg"
      />
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0 w-full h-full pointer-events-none"
      />
      {eyeTrackingActive && (
        <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded text-sm flex items-center">
          <div className="w-2 h-2 bg-white rounded-full mr-1 animate-pulse"></div>
          Eye Tracking
        </div>
      )}
      {isRecording && (
        <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded text-sm flex items-center">
          <div className="w-2 h-2 bg-white rounded-full mr-1 animate-pulse"></div>
          Recording
        </div>
      )}
    </div>
  );
};

export default VideoRecorder;
