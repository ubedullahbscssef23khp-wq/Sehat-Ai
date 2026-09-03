/** UI chrome strings for en / ur / sd.
 *
 * These are interface labels only. All medical guidance, triage wording,
 * follow-up questions, evidence, and disclaimers come from the backend and are
 * rendered verbatim — the frontend never generates or translates medical copy.
 * Starter prompts are benign UI examples, not diagnoses.
 */

import type { Language, TriageLevel } from "../api/types";

export const LANGUAGES: readonly { code: Language; label: string; dir: "ltr" | "rtl" }[] = [
  { code: "en", label: "English", dir: "ltr" },
  { code: "ur", label: "اردو", dir: "rtl" },
  { code: "sd", label: "سنڌي", dir: "rtl" },
];

export function directionOf(language: Language): "ltr" | "rtl" {
  return language === "en" ? "ltr" : "rtl";
}

export interface StringTable {
  appName: string;
  tagline: string;
  heroTitle: string;
  heroSubtitle: string;
  starterHeading: string;
  inputPlaceholder: string;
  send: string;
  newConversation: string;
  languageLabel: string;
  thinking: string;
  assistantName: string;
  followUpHeading: string;
  evidenceHeading: string;
  reviewedOn: string;
  disclaimerHeading: string;
  limitedConfidence: string;
  errorOffline: string;
  errorServer: string;
  errorValidation: string;
  errorTooLong: string;
  errorClosed: string;
  errorNotFound: string;
  errorUnavailable: string;
  errorGeneric: string;
  retry: string;
  sessionEnded: string;
  youLabel: string;
  disclaimerText: string;
  triageLabels: Record<TriageLevel, string>;
}

const en: StringTable = {
  appName: "Sehat AI",
  tagline: "AI-assisted health guidance and symptom triage",
  heroTitle: "Understand your symptoms. Get guided next steps.",
  heroSubtitle:
    "Describe how you feel in your own words. Sehat AI asks focused questions and suggests the right next step — it does not diagnose and never replaces a healthcare professional.",
  starterHeading: "You could start with",
  inputPlaceholder: "Describe your symptoms…",
  send: "Send",
  newConversation: "New conversation",
  languageLabel: "Language",
  thinking: "Sehat AI is thinking…",
  assistantName: "Sehat AI",
  followUpHeading: "One more thing would help me understand this better",
  evidenceHeading: "Information sources",
  reviewedOn: "Reviewed",
  disclaimerHeading: "Important",
  limitedConfidence:
    "This guidance is based on limited information. If you are worried, or symptoms worsen, seek medical care.",
  errorOffline: "Sehat AI could not be reached. Please check your connection and try again.",
  errorServer: "Something went wrong on our side. Please try again in a moment.",
  errorValidation: "Please enter a message before sending.",
  errorTooLong: "Your message is too long. Please shorten it and try again.",
  errorClosed: "This conversation has ended. Start a new conversation to continue.",
  errorNotFound: "That conversation could not be found. Start a new conversation to continue.",
  errorUnavailable: "Sehat AI is temporarily unable to process this message. Please try again shortly.",
  errorGeneric: "Something went wrong. Please try again.",
  retry: "Try again",
  sessionEnded: "This conversation has ended.",
  youLabel: "You",
  disclaimerText:
    "Sehat AI provides general next-step guidance only. It is not a medical diagnosis and does not replace a qualified healthcare professional.",
  triageLabels: {
    emergency: "Seek emergency care now",
    urgent_same_day: "See a professional today",
    routine: "Arrange a routine review",
    self_care: "Self-care at home",
    needs_more_info: "A few more details needed",
  },
};

const ur: StringTable = {
  appName: "صحت اے آئی",
  tagline: "مصنوعی ذہانت پر مبنی صحت رہنمائی اور علامات کی جانچ",
  heroTitle: "اپنی علامات سمجھیں۔ اگلے قدم کی رہنمائی پائیں۔",
  heroSubtitle:
    "اپنے الفاظ میں بتائیں کہ آپ کیسا محسوس کر رہے ہیں۔ صحت اے آئی چند اہم سوالات پوچھ کر مناسب اگلا قدم تجویز کرتا ہے — یہ تشخیص نہیں کرتا اور کبھی بھی ڈاکٹر کا متبادل نہیں۔",
  starterHeading: "آپ اس طرح شروع کر سکتے ہیں",
  inputPlaceholder: "اپنی علامات بیان کریں…",
  send: "بھیجیں",
  newConversation: "نئی گفتگو",
  languageLabel: "زبان",
  thinking: "صحت اے آئی سوچ رہا ہے…",
  assistantName: "صحت اے آئی",
  followUpHeading: "بہتر رہنمائی کے لیے ایک اور معلومات درکار ہے",
  evidenceHeading: "معلومات کے ذرائع",
  reviewedOn: "جائزہ لیا گیا",
  disclaimerHeading: "اہم",
  limitedConfidence:
    "یہ رہنمائی محدود معلومات پر مبنی ہے۔ اگر آپ کو تشویش ہو یا علامات بڑھیں تو طبی مدد حاصل کریں۔",
  errorOffline: "صحت اے آئی سے رابطہ نہیں ہو سکا۔ براہ کرم اپنا کنکشن جانچ کر دوبارہ کوشش کریں۔",
  errorServer: "ہماری طرف سے ایک مسئلہ پیش آیا۔ براہ کرم کچھ دیر بعد دوبارہ کوشش کریں۔",
  errorValidation: "براہ کرم بھیجنے سے پہلے پیغام لکھیں۔",
  errorTooLong: "آپ کا پیغام بہت لمبا ہے۔ براہ کرم اسے چھوٹا کر کے دوبارہ کوشش کریں۔",
  errorClosed: "یہ گفتگو ختم ہو چکی ہے۔ جاری رکھنے کے لیے نئی گفتگو شروع کریں۔",
  errorNotFound: "وہ گفتگو نہیں ملی۔ جاری رکھنے کے لیے نئی گفتگو شروع کریں۔",
  errorUnavailable: "صحت اے آئی عارضی طور پر یہ پیغام پروسیس نہیں کر سکتا۔ براہ کرم جلد دوبارہ کوشش کریں۔",
  errorGeneric: "کچھ غلط ہو گیا۔ براہ کرم دوبارہ کوشش کریں۔",
  retry: "دوبارہ کوشش کریں",
  sessionEnded: "یہ گفتگو ختم ہو چکی ہے۔",
  youLabel: "آپ",
  disclaimerText:
    "صحت اے آئی صرف عمومی اگلے قدم کی رہنمائی فراہم کرتا ہے۔ یہ طبی تشخیص نہیں ہے اور کسی مستند طبی پیشہ ور کا متبادل نہیں۔",
  triageLabels: {
    emergency: "ابھی ایمرجنسی طبی مدد حاصل کریں",
    urgent_same_day: "آج ہی کسی ماہر کو دکھائیں",
    routine: "عام معائنہ کروائیں",
    self_care: "گھر پر اپنی دیکھ بھال کریں",
    needs_more_info: "کچھ مزید معلومات درکار ہیں",
  },
};

const sd: StringTable = {
  appName: "صحت اي آءِ",
  tagline: "مصنوعي ذهانت تي ٻڌل صحت رهنمائي ۽ علامتن جي جانچ",
  heroTitle: "پنهنجي علامتن کي سمجهو. ايندڙ قدم جي رهنمائي حاصل ڪريو.",
  heroSubtitle:
    "پنهنجن لفظن ۾ ٻڌايو ته توهان ڪيئن محسوس ڪري رهيا آهيو. صحت اي آءِ ڪجهه اهم سوال پڇي مناسب ايندڙ قدم تجويز ڪري ٿو — هي تشخيص نٿو ڪري ۽ ڪڏهن به ڊاڪٽر جو متبادل ناهي.",
  starterHeading: "توهان هن ريت شروع ڪري سگهو ٿا",
  inputPlaceholder: "پنهنجي علامتون بيان ڪريو…",
  send: "موڪليو",
  newConversation: "نئين ڳالهه ٻولهه",
  languageLabel: "ٻولي",
  thinking: "صحت اي آءِ سوچي رهيو آهي…",
  assistantName: "صحت اي آءِ",
  followUpHeading: "بهتر رهنمائي لاءِ هڪ وڌيڪ معلومات گهربل آهي",
  evidenceHeading: "معلومات جا ذريعا",
  reviewedOn: "جائزو ورتو ويو",
  disclaimerHeading: "اهم",
  limitedConfidence:
    "هي رهنمائي محدود معلومات تي ٻڌل آهي. جيڪڏهن توهان کي پريشاني هجي يا علامتون وڌن ته طبي مدد وٺو.",
  errorOffline: "صحت اي آءِ سان رابطو نه ٿي سگهيو. مهرباني ڪري پنهنجو ڪنيڪشن چيڪ ڪري ٻيهر ڪوشش ڪريو.",
  errorServer: "اسان جي طرف کان هڪ مسئلو پيش آيو. مهرباني ڪري ٿوري دير بعد ٻيهر ڪوشش ڪريو.",
  errorValidation: "مهرباني ڪري موڪلڻ کان پهريان پيغام لکو.",
  errorTooLong: "توهان جو پيغام تمام ڊگهو آهي. مهرباني ڪري ان کي ننڍو ڪري ٻيهر ڪوشش ڪريو.",
  errorClosed: "هي ڳالهه ٻولهه ختم ٿي چڪي آهي. جاري رکڻ لاءِ نئين ڳالهه ٻولهه شروع ڪريو.",
  errorNotFound: "اها ڳالهه ٻولهه نه ملي. جاري رکڻ لاءِ نئين ڳالهه ٻولهه شروع ڪريو.",
  errorUnavailable: "صحت اي آءِ عارضي طور تي هي پيغام پروسيس نٿو ڪري سگهي. مهرباني ڪري جلد ٻيهر ڪوشش ڪريو.",
  errorGeneric: "ڪجهه غلط ٿي ويو. مهرباني ڪري ٻيهر ڪوشش ڪريو.",
  retry: "ٻيهر ڪوشش ڪريو",
  sessionEnded: "هي ڳالهه ٻولهه ختم ٿي چڪي آهي.",
  youLabel: "توهان",
  disclaimerText:
    "صحت اي آءِ صرف عام ايندڙ قدم جي رهنمائي مهيا ڪري ٿو. هي طبي تشخيص ناهي ۽ ڪنهن مستند طبي ماهر جو متبادل ناهي.",
  triageLabels: {
    emergency: "هاڻي ايمرجنسي طبي مدد وٺو",
    urgent_same_day: "اڄ ئي ڪنهن ماهر کي ڏيکاريو",
    routine: "عام معائنو ڪرايو",
    self_care: "گهر تي پنهنجي سنڀال ڪريو",
    needs_more_info: "ڪجهه وڌيڪ معلومات گهربل آهي",
  },
};

const TABLES: Record<Language, StringTable> = { en, ur, sd };

export function strings(language: Language): StringTable {
  return TABLES[language];
}

/** Benign UI example prompts only — never medical advice or diagnoses. */
export const STARTER_PROMPTS: { key: string; text: Record<Language, string> }[] = [
  {
    key: "headache",
    text: {
      en: "I have a headache since yesterday",
      ur: "کل سے میرے سر میں درد ہے",
      sd: "ڪالهه کان منهنجي سر ۾ سور آهي",
    },
  },
  {
    key: "tired",
    text: {
      en: "I've been feeling unusually tired",
      ur: "میں غیر معمولی طور پر تھکاوٹ محسوس کر رہا ہوں",
      sd: "مان غير معمولي طور تي ٿڪاوٽ محسوس ڪري رهيو آهيان",
    },
  },
  {
    key: "throat",
    text: {
      en: "I have a sore throat and fever",
      ur: "میرے گلے میں درد اور بخار ہے",
      sd: "منهنجي گلي ۾ سور ۽ تپ آهي",
    },
  },
];
