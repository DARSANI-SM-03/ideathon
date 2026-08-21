import React, { useState, useEffect } from 'react';
import { Volume2, VolumeX, Play, Square, Globe, Sparkles } from 'lucide-react';

interface ParentVoiceSummaryProps {
  studentName: string;
  eduMins: number;
  prodMins: number;
  entMins: number;
  gameMins: number;
  focusScore: number;
  burnoutScore: number;
  burnoutLevel: string;
}

export type SupportedLanguage = 'en' | 'hi' | 'ta' | 'kn' | 'te' | 'ml';

export const ParentVoiceSummary: React.FC<ParentVoiceSummaryProps> = ({
  studentName,
  eduMins,
  prodMins,
  entMins,
  gameMins,
  focusScore,
  burnoutScore,
  burnoutLevel
}) => {
  const [lang, setLang] = useState<SupportedLanguage>('en');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSupported, setIsSupported] = useState(true);

  useEffect(() => {
    if (!('speechSynthesis' in window)) {
      setIsSupported(false);
    }
  }, []);

  const formatHoursMinsStr = (totalMins: number, l: SupportedLanguage) => {
    const hrs = Math.floor(totalMins / 60);
    const mins = totalMins % 60;
    if (l === 'hi') return hrs > 0 ? `${hrs} घंटे ${mins} मिनट` : `${mins} मिनट`;
    if (l === 'ta') return hrs > 0 ? `${hrs} மணிநேரம் ${mins} நிமிடங்கள்` : `${mins} நிமிடங்கள்`;
    if (l === 'kn') return hrs > 0 ? `${hrs} ಗಂಟೆ ${mins} ನಿಮಿಷಗಳು` : `${mins} ನಿಮಿಷಗಳು`;
    if (l === 'te') return hrs > 0 ? `${hrs} గంటల ${mins} నిమిషాలు` : `${mins} నిమిషాలు`;
    if (l === 'ml') return hrs > 0 ? `${hrs} മണിക്കൂർ ${mins} മിനിറ്റ്` : `${mins} മിനിറ്റ്`;
    return hrs > 0 ? `${hrs} hours and ${mins} minutes` : `${mins} minutes`;
  };

  const getBurnoutText = (level: string, l: SupportedLanguage) => {
    const lvl = (level || 'low').toLowerCase();
    if (l === 'ta') {
      if (lvl === 'low') return 'குறைவாக (Low)';
      if (lvl === 'moderate') return 'மிதமாக (Moderate)';
      if (lvl === 'high') return 'அதிகமாக (High)';
      if (lvl === 'critical') return 'மிக ஆபத்தான (Critical)';
      return level;
    }
    if (l === 'hi') {
      if (lvl === 'low') return 'कम (Low)';
      if (lvl === 'moderate') return 'मध्यम (Moderate)';
      if (lvl === 'high') return 'उच्च (High)';
      if (lvl === 'critical') return 'गंभीर (Critical)';
      return level;
    }
    if (l === 'kn') {
      if (lvl === 'low') return 'ಕಡಿಮೆ (Low)';
      if (lvl === 'moderate') return 'ಮಧ್ಯಮ (Moderate)';
      if (lvl === 'high') return 'ಹೆಚ್ಚು (High)';
      if (lvl === 'critical') return 'ಗಂಭೀರ (Critical)';
      return level;
    }
    if (l === 'te') {
      if (lvl === 'low') return 'తక్కువ (Low)';
      if (lvl === 'moderate') return 'మధ్యస్థం (Moderate)';
      if (lvl === 'high') return 'ఎక్కువ (High)';
      if (lvl === 'critical') return 'తీవ్రమైన (Critical)';
      return level;
    }
    if (l === 'ml') {
      if (lvl === 'low') return 'കുറഞ്ഞ (Low)';
      if (lvl === 'moderate') return 'മിതമായ (Moderate)';
      if (lvl === 'high') return 'കൂടിയ (High)';
      if (lvl === 'critical') return 'തീവ്രമായ (Critical)';
      return level;
    }
    return level;
  };

  const generateSummaryText = (l: SupportedLanguage) => {
    const totalStudy = eduMins + prodMins;
    const eduStr = formatHoursMinsStr(eduMins, l);
    const prodStr = formatHoursMinsStr(prodMins, l);
    const entStr = formatHoursMinsStr(entMins, l);
    const totalStudyStr = formatHoursMinsStr(totalStudy, l);
    const burnoutStr = getBurnoutText(burnoutLevel, l);

    switch (l) {
      case 'hi':
        return `आज आपके बच्चे ${studentName} ने कुल ${totalStudyStr} पढ़ाई और उत्पादक गतिविधियों में बिताए। इसमें से ${eduStr} शैक्षणिक कार्यों में, ${prodStr} उत्पादक कार्यों में और ${entStr} मनोरंजन में बिताए गए। वर्तमान एकाग्रता स्कोर ${Math.round(focusScore)}% है और बर्नआउट जोखिम ${burnoutStr} है।`;

      case 'ta':
        return `இன்று உங்கள் குழந்தை ${studentName} மொத்தம் ${totalStudyStr} படிப்பு மற்றும் பயனுள்ள பணிகளில் செலவிட்டார். இதில் ${eduStr} கல்விப் பணிகளுக்கும், ${prodStr} பயனுள்ள செயல்பாடுகளுக்கும், ${entStr} பொழுதுபோக்கிற்கும் செலவிடப்பட்டது. நேரடி கவனக் குறியீடு ${Math.round(focusScore)}% ஆகவும், மனஅழுத்த அபாய அளவு ${burnoutStr} ஆகவும் உள்ளது.`;

      case 'kn':
        return `ಇಂದು ನಿಮ್ಮ ಮಗು ${studentName} ಒಟ್ಟು ${totalStudyStr} ಅಧ್ಯಯನ ಮತ್ತು ಉಪಯುಕ್ತ ಕೆಲಸಗಳಲ್ಲಿ ವಿನಿಯೋಗಿಸಿದೆ. ಇದರಲ್ಲಿ ${eduStr} ಶೈಕ್ಷಣಿಕ ಕಾರ್ಯಗಳಿಗೆ, ${prodStr} ಉತ್ಪಾದಕ ಕೆಲಸಗಳಿಗೆ ಮತ್ತು ${entStr} ಮನರಂಜನೆಗೆ ವಿನಿಯೋಗಿಸಲಾಗಿದೆ. ಪ್ರಸ್ತುತ ಗಮನದ ಅಂಕ ${Math.round(focusScore)}% ಆಗಿದ್ದು, ಆಯಾಸದ ಅಪಾಯ ${burnoutStr} ಆಗಿದೆ.`;

      case 'te':
        return `ఈరోజు మీ పిల్లవాడు ${studentName} మొత్తం ${totalStudyStr} చదువు మరియు ఉపయోగకరమైన పనులలో గడిపారు. ఇందులో ${eduStr} విద్యా విషయాలకు, ${prodStr} ఉపయోగకరమైన పనులకు మరియు ${entStr} వినోదానికి కేటాయించబడింది. ప్రస్తుత శ్రద్ధ స్కోరు ${Math.round(focusScore)}% కాగా, అలసట ప్రమాదం ${burnoutStr}గా ఉంది.`;

      case 'ml':
        return `ഇന്ന് നിങ്ങളുടെ കുട്ടി ${studentName} ആകെ ${totalStudyStr} പഠനത്തിലും പ്രയോജനപ്രദമായ പ്രവർത്തനങ്ങളിലും ചെലവഴിച്ചു. ഇതിൽ ${eduStr} വിദ്യാഭ്യാസ ആവശ്യങ്ങൾക്കും, ${prodStr} പ്രയോജനപ്രദമായ ജോലികൾക്കും, ${entStr} വിനോദത്തിനുമായി ചെലവഴിച്ചു. നിലവിലെ ശ്രദ്ധ സ്കോർ ${Math.round(focusScore)}% ഉം, ബേൺഔട്ട് സാധ്യത ${burnoutStr} തലത്തിലുമാണ്.`;

      default:
        return `Today your child ${studentName} studied for ${totalStudyStr}. ${eduStr} were educational, ${prodStr} were productive, and ${entStr} were spent on entertainment. The live focus score is ${Math.round(focusScore)}%, and burnout risk level is ${burnoutLevel}.`;
    }
  };

  const langCodeMap: Record<SupportedLanguage, string> = {
    en: 'en-US',
    hi: 'hi-IN',
    ta: 'ta-IN',
    kn: 'kn-IN',
    te: 'te-IN',
    ml: 'ml-IN'
  };

  const handlePlayVoice = () => {
    if (!isSupported) return;

    window.speechSynthesis.cancel();

    if (isPlaying) {
      setIsPlaying(false);
      return;
    }

    const textToSpeak = generateSummaryText(lang);
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.lang = langCodeMap[lang];
    utterance.rate = 0.95;

    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);

    setIsPlaying(true);
    window.speechSynthesis.speak(utterance);
  };

  const summaryPreview = generateSummaryText(lang);

  return (
    <div className="glass-card rounded-2xl p-5 border border-brand-500/30 bg-gradient-to-r from-slate-900 via-brand-950/20 to-slate-900 space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 text-brand-400 flex items-center justify-center">
            <Volume2 className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Parent AI Voice Summary <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            </h3>
            <p className="text-[11px] text-slate-400">Spoken audio summary generated live from Desktop Agent telemetry.</p>
          </div>
        </div>

        {/* Multi-Language Selector */}
        <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
          <Globe className="w-3.5 h-3.5 text-brand-400" />
          <span className="text-slate-400 font-medium">Language:</span>
          <select
            value={lang}
            onChange={(e) => {
              setLang(e.target.value as SupportedLanguage);
              if (isPlaying) window.speechSynthesis.cancel();
              setIsPlaying(false);
            }}
            className="bg-transparent text-white font-bold focus:outline-none cursor-pointer"
          >
            <option value="en" className="bg-slate-900 text-white">English (en-US)</option>
            <option value="hi" className="bg-slate-900 text-white">हिन्दी - Hindi (hi-IN)</option>
            <option value="ta" className="bg-slate-900 text-white">தமிழ் - Tamil (ta-IN)</option>
            <option value="kn" className="bg-slate-900 text-white">ಕನ್ನಡ - Kannada (kn-IN)</option>
            <option value="te" className="bg-slate-900 text-white">తెలుగు - Telugu (te-IN)</option>
            <option value="ml" className="bg-slate-900 text-white">മലയാളം - Malayalam (ml-IN)</option>
          </select>
        </div>
      </div>

      <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs text-slate-300 font-sans leading-relaxed italic">
        "{summaryPreview}"
      </div>

      <div className="flex items-center justify-between pt-1">
        <button
          onClick={handlePlayVoice}
          className={`px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition shadow-lg ${
            isPlaying
              ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-500/20'
              : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-500/20'
          }`}
        >
          {isPlaying ? (
            <>
              <Square className="w-4 h-4" /> Stop Voice Summary
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" /> ▶ Play Today's Spoken Summary
            </>
          )}
        </button>

        <span className="text-[11px] font-mono text-slate-400">
          Selected Voice: {langCodeMap[lang]}
        </span>
      </div>
    </div>
  );
};
