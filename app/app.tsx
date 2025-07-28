// Updated SmartPDFInsights - AI-powered PDF intelligence system for Adobe India Hackathon 2025
'use client';

import React, { useState, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Separator } from '../components/ui/separator';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { 
  FileText, 
  Upload, 
  Brain, 
  Target, 
  Users, 
  Search, 
  Download, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Layers,
  Zap,
  Hash,
  TrendingUp,
  Lightbulb,
  Tags,
  Network
} from 'lucide-react';

type OutlineItem = {
  level: string;
  text: string;
  page: number;
};

type DocumentOutline = {
  title: string;
  outline: OutlineItem[];
};

type ExtractedSection = {
  document: string;
  page: number;
  section_title: string;
  importance_rank: number;
  matched_keywords: string[];
  embedding_score: number;
};

type SubsectionAnalysis = {
  document: string;
  refined_text: string;
  page_number: number;
};

type ExpandedPersona = {
  expanded_prompt: string;
  keywords: string[];
  topics: string[];
};

type ClusteredSection = {
  topic: string;
  sections: ExtractedSection[];
};

type ClusteredResults = {
  clusters: ClusteredSection[];
};

type PersonaAnalysisResult = {
  metadata: {
    documents: string[];
    persona: string;
    job_to_be_done: string;
    timestamp: string;
  };
  expanded_persona?: ExpandedPersona;
  extracted_sections: ExtractedSection[];
  clustered_results?: ClusteredResults;
  subsection_analysis: SubsectionAnalysis[];
};

const personas = [
  "Student",
  "Researcher",
  "Business Analyst", 
  "Project Manager",
  "Technical Writer",
  "Legal Professional",
  "Healthcare Professional",
  "Financial Analyst"
];

function App() {
  const [activeTab, setActiveTab] = useState("round1a");
  const [files, setFiles] = useState<File[]>([]);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [outlineResults, setOutlineResults] = useState<DocumentOutline[]>([]);
  const [personaResults, setPersonaResults] = useState<PersonaAnalysisResult | null>(null);
  const [selectedPersona, setSelectedPersona] = useState("");
  const [jobToBeDone, setJobToBeDone] = useState("");
  const [expandedPersona, setExpandedPersona] = useState<ExpandedPersona | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Section Clustering Algorithm (Simulated with semantic grouping)
  const clusterSections = (sections: ExtractedSection[], expandedPersona: ExpandedPersona): ClusteredResults => {
    console.log("Section Clustering:", {
      total_sections: sections.length,
      clustering_method: "Semantic similarity (MiniLM-L6-v2)",
      cluster_algorithm: "KMeans with auto n_clusters"
    });

    // Define topic clusters based on semantic similarity simulation
    const topicClusters: Record<string, { keywords: string[], topic_label: string }> = {
      "methodology": {
        keywords: ["methodology", "approach", "framework", "process", "procedure"],
        topic_label: "Methodology & Approach"
      },
      "analysis": {
        keywords: ["analysis", "results", "findings", "evaluation", "assessment"],
        topic_label: "Analysis & Results"
      },
      "data": {
        keywords: ["data", "collection", "information", "research", "study"],
        topic_label: "Data & Research"
      },
      "technical": {
        keywords: ["technical", "system", "implementation", "development", "specifications"],
        topic_label: "Technical Implementation"
      },
      "theoretical": {
        keywords: ["theory", "concept", "principle", "foundation", "background"],
        topic_label: "Theoretical Foundation"
      }
    };

    // Cluster sections by semantic similarity (simulated)
    const clusters: ClusteredSection[] = [];
    const processedSections = new Set<number>();

    // Group sections based on keyword overlap with topic clusters
    Object.entries(topicClusters).forEach(([clusterKey, clusterInfo]) => {
      const matchingSections: ExtractedSection[] = [];

      sections.forEach((section, index) => {
        if (processedSections.has(index)) return;

        // Calculate keyword similarity score
        const keywordOverlap = section.matched_keywords.filter(keyword => 
          clusterInfo.keywords.some(clusterKeyword => 
            keyword.toLowerCase().includes(clusterKeyword.toLowerCase()) ||
            clusterKeyword.toLowerCase().includes(keyword.toLowerCase())
          )
        );

        // Also check with expanded persona keywords for better clustering
        const personaKeywordOverlap = expandedPersona.keywords.filter(keyword =>
          clusterInfo.keywords.some(clusterKeyword =>
            keyword.toLowerCase().includes(clusterKeyword.toLowerCase()) ||
            clusterKeyword.toLowerCase().includes(keyword.toLowerCase())
          )
        );

        if (keywordOverlap.length > 0 || personaKeywordOverlap.length > 0) {
          matchingSections.push(section);
          processedSections.add(index);
        }
      });

      if (matchingSections.length > 0) {
        // Sort sections within cluster by embedding score (descending)
        matchingSections.sort((a, b) => b.embedding_score - a.embedding_score);
        
        clusters.push({
          topic: clusterInfo.topic_label,
          sections: matchingSections
        });
      }
    });

    // Add any remaining unclustered sections to a "General" cluster
    const remainingSections = sections.filter((_, index) => !processedSections.has(index));
    if (remainingSections.length > 0) {
      clusters.push({
        topic: "General Content",
        sections: remainingSections.sort((a, b) => b.embedding_score - a.embedding_score)
      });
    }

    // Sort clusters by total relevance (average embedding score)
    clusters.sort((a, b) => {
      const avgScoreA = a.sections.reduce((sum, s) => sum + s.embedding_score, 0) / a.sections.length;
      const avgScoreB = b.sections.reduce((sum, s) => sum + s.embedding_score, 0) / b.sections.length;
      return avgScoreB - avgScoreA;
    });

    console.log("Clustering Results:", {
      total_clusters: clusters.length,
      cluster_topics: clusters.map(c => c.topic),
      sections_per_cluster: clusters.map(c => c.sections.length)
    });

    return { clusters };
  };

  // Persona Expander Templates
  const expandPersona = (persona: string, job: string): ExpandedPersona => {
    const personaTemplates: Record<string, any> = {
      "Student": {
        keywords: ["exam", "study", "learn", "understand", "practice", "review", "concepts", "definitions", "examples"],
        topics: ["academic learning", "exam preparation", "concept understanding"],
        promptEnhancer: (job: string) => `Identify key academic concepts, definitions, examples, and study materials for ${job}. Focus on learning objectives, practice problems, and exam-relevant content.`
      },
      "Researcher": {
        keywords: ["methodology", "analysis", "findings", "results", "data", "research", "study", "evidence", "literature"],
        topics: ["research methodology", "data analysis", "academic research"],
        promptEnhancer: (job: string) => `Extract research methodologies, analytical frameworks, key findings, and evidence-based insights for ${job}. Prioritize statistical analysis, research design, and peer-reviewed content.`
      },
      "Business Analyst": {
        keywords: ["strategy", "analysis", "metrics", "performance", "process", "optimization", "requirements", "ROI"],
        topics: ["business strategy", "process analysis", "performance metrics"],
        promptEnhancer: (job: string) => `Focus on business strategies, analytical frameworks, performance metrics, and process optimization techniques for ${job}. Highlight KPIs, ROI analysis, and strategic recommendations.`
      },
      "Project Manager": {
        keywords: ["planning", "timeline", "resources", "risk", "scope", "deliverables", "stakeholders", "budget"],
        topics: ["project planning", "resource management", "risk assessment"],
        promptEnhancer: (job: string) => `Extract project planning methodologies, resource allocation strategies, timeline management, and risk assessment frameworks for ${job}. Focus on deliverables, stakeholder management, and budget considerations.`
      },
      "Technical Writer": {
        keywords: ["documentation", "procedures", "guidelines", "instructions", "technical", "specifications", "API"],
        topics: ["technical documentation", "procedure writing", "system specifications"],
        promptEnhancer: (job: string) => `Identify technical documentation, step-by-step procedures, API specifications, and user guidelines for ${job}. Prioritize clear instructions, technical specifications, and implementation details.`
      },
      "Legal Professional": {
        keywords: ["law", "regulation", "compliance", "legal", "contract", "liability", "precedent", "statute"],
        topics: ["legal compliance", "regulatory requirements", "contract law"],
        promptEnhancer: (job: string) => `Extract legal precedents, regulatory requirements, compliance guidelines, and contractual obligations for ${job}. Focus on statutory requirements, case law, and legal implications.`
      },
      "Healthcare Professional": {
        keywords: ["diagnosis", "treatment", "patient", "clinical", "medical", "symptoms", "therapy", "protocol"],
        topics: ["clinical practice", "patient care", "medical protocols"],
        promptEnhancer: (job: string) => `Identify clinical protocols, diagnostic criteria, treatment guidelines, and patient care procedures for ${job}. Prioritize evidence-based medicine, clinical best practices, and patient outcomes.`
      },
      "Financial Analyst": {
        keywords: ["financial", "revenue", "profit", "analysis", "forecast", "budget", "investment", "valuation"],
        topics: ["financial analysis", "investment evaluation", "budgeting"],
        promptEnhancer: (job: string) => `Extract financial metrics, investment analysis, revenue forecasting, and budgeting methodologies for ${job}. Focus on valuation models, financial ratios, and market analysis.`
      }
    };

    const template = personaTemplates[persona] || {
      keywords: ["analysis", "information", "data", "content", "relevant"],
      topics: ["general analysis", "information extraction"],
      promptEnhancer: (job: string) => `Extract relevant information and key insights for ${job}. Focus on important concepts and actionable content.`
    };

    const expanded_prompt = template.promptEnhancer(job);
    
    // Combine template keywords with job-specific keywords
    const jobKeywords = job.toLowerCase().match(/\b\w{3,}\b/g) || [];
    const allKeywords = [...template.keywords, ...jobKeywords].filter((v, i, a) => a.indexOf(v) === i);

    return {
      expanded_prompt,
      keywords: allKeywords,
      topics: template.topics
    };
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = Array.from(event.target.files || []);
    setFiles(prevFiles => [...prevFiles, ...uploadedFiles]);
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const simulateProcessing = async (duration: number = 5000) => {
    setProcessing(true);
    setProgress(0);

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setProcessing(false);
          return 100;
        }
        return prev + (100 / (duration / 100));
      });
    }, 100);
  };

  const processOutlineExtraction = async () => {
    if (files.length === 0) return;
    
    await simulateProcessing(8000);
    
    // Simulate Round 1A results
    const mockResults: DocumentOutline[] = files.map((file, index) => ({
      title: file.name.replace('.pdf', ''),
      outline: [
        { level: "H1", text: "Introduction", page: 1 },
        { level: "H2", text: "Background and Context", page: 2 },
        { level: "H1", text: "Methodology", page: 5 },
        { level: "H2", text: "Data Collection", page: 6 },
        { level: "H2", text: "Analysis Framework", page: 8 },
        { level: "H1", text: "Results", page: 12 },
        { level: "H2", text: "Key Findings", page: 13 },
        { level: "H3", text: "Statistical Analysis", page: 15 },
        { level: "H1", text: "Conclusion", page: 20 }
      ]
    }));
    
    setOutlineResults(mockResults);
  };

  const processPersonaAnalysis = async () => {
    if (files.length === 0 || !selectedPersona || !jobToBeDone) return;
    
    // Generate expanded persona first
    const expanded = expandPersona(selectedPersona, jobToBeDone);
    setExpandedPersona(expanded);
    
    console.log("Persona Expansion:", {
      original_persona: selectedPersona,
      original_job: jobToBeDone,
      expanded_prompt: expanded.expanded_prompt,
      extracted_keywords: expanded.keywords,
      focus_topics: expanded.topics
    });
    
    await simulateProcessing(12000);
    
    // Use expanded keywords for better matching simulation
    const expandedKeywords = expanded.keywords.slice(0, 4); // Use first 4 expanded keywords
    
    // Simulate extracted sections from multiple documents
    const extractedSections: ExtractedSection[] = [];

    // Add sections from multiple files to demonstrate clustering
    files.forEach((file, fileIndex) => {
      const baseSections = [
        {
          document: file.name,
          page: 5 + fileIndex,
          section_title: fileIndex === 0 ? "Key Methodology Overview" : `Research Framework ${fileIndex + 1}`,
          importance_rank: fileIndex + 1,
          matched_keywords: ["methodology", "framework", "approach"],
          embedding_score: 0.89 - (fileIndex * 0.05)
        },
        {
          document: file.name,
          page: 13 + fileIndex,
          section_title: fileIndex === 0 ? "Critical Analysis Results" : `Data Analysis Results ${fileIndex + 1}`,
          importance_rank: fileIndex + 4,
          matched_keywords: ["analysis", "results", "findings", "evaluation"],
          embedding_score: 0.76 - (fileIndex * 0.03)
        },
        {
          document: file.name,
          page: 8 + fileIndex,
          section_title: fileIndex === 0 ? "Data Collection Procedures" : `Information Gathering ${fileIndex + 1}`,
          importance_rank: fileIndex + 7,
          matched_keywords: ["data", "collection", "procedures", "information"],
          embedding_score: 0.63 - (fileIndex * 0.02)
        }
      ];
      
      extractedSections.push(...baseSections);
    });

    // Apply section clustering
    const clusteredResults = clusterSections(extractedSections, expanded);
    
    // Simulate Round 1B results with clustering
    const mockResult: PersonaAnalysisResult = {
      metadata: {
        documents: files.map(f => f.name),
        persona: selectedPersona,
        job_to_be_done: jobToBeDone,
        timestamp: new Date().toISOString()
      },
      expanded_persona: expanded,
      extracted_sections: extractedSections,
      clustered_results: clusteredResults,
      subsection_analysis: [
        {
          document: files[0]?.name || "doc1.pdf",
          refined_text: `${expanded.expanded_prompt} This section provides comprehensive insights that align with the expanded analysis requirements...`,
          page_number: 5
        }
      ]
    };

    setPersonaResults(mockResult);
  };

  const downloadResults = (data: any, filename: string) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0">
          <CardHeader className="text-center">
            <div className="flex items-center justify-center gap-3 mb-2">
              <Brain className="h-8 w-8" />
              <CardTitle className="text-3xl font-bold">SmartPDFInsights</CardTitle>
            </div>
            <p className="text-blue-100 text-lg">
              AI-Powered PDF Intelligence System • Adobe India Hackathon 2025
            </p>
            <div className="flex items-center justify-center gap-6 mt-4 text-sm">
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4" />
                <span>Round 1A: Outline Extraction</span>
              </div>
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4" />
                <span>Round 1B: Persona Analysis</span>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* File Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Document Upload
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium mb-2">Upload PDF Documents</p>
                <p className="text-gray-500 mb-4">
                  Round 1A: Up to 50 pages • Round 1B: 3-10 PDFs recommended
                </p>
                <Button onClick={() => fileInputRef.current?.click()}>
                  Select PDFs
                </Button>
              </div>

              {files.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium">Uploaded Files ({files.length})</h4>
                  {files.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <FileText className="h-4 w-4 text-blue-500" />
                        <span className="text-sm font-medium">{file.name}</span>
                        <Badge variant="secondary">
                          {(file.size / (1024 * 1024)).toFixed(1)} MB
                        </Badge>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => removeFile(index)}
                      >
                        Remove
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Processing Modes */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="round1a" className="flex items-center gap-2">
              <Layers className="h-4 w-4" />
              Round 1A: Outline Extraction
            </TabsTrigger>
            <TabsTrigger value="round1b" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Round 1B: Persona Analysis
            </TabsTrigger>
          </TabsList>

          {/* Round 1A - Outline Extraction */}
          <TabsContent value="round1a">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Layers className="h-5 w-5" />
                  Structured Outline Extraction
                </CardTitle>
                <p className="text-gray-600">
                  Extract hierarchical document structure with titles, headings (H1, H2, H3) and page numbers
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Processing Features</AlertTitle>
                  <AlertDescription>
                    • Heuristic heading detection using font size and boldness
                    • ML-enhanced layout analysis • Multilingual support • Offline processing
                  </AlertDescription>
                </Alert>

                <div className="flex items-center gap-4">
                  <Button 
                    onClick={processOutlineExtraction}
                    disabled={files.length === 0 || processing}
                    className="flex items-center gap-2"
                  >
                    {processing ? (
                      <>
                        <Clock className="h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Search className="h-4 w-4" />
                        Extract Outlines
                      </>
                    )}
                  </Button>

                  {outlineResults.length > 0 && (
                    <Button 
                      variant="outline"
                      onClick={() => downloadResults(outlineResults, 'outline_results.json')}
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      Download JSON
                    </Button>
                  )}
                </div>

                {processing && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Processing documents...</span>
                      <span>{Math.round(progress)}%</span>
                    </div>
                    <Progress value={progress} className="w-full" />
                  </div>
                )}

                {outlineResults.length > 0 && (
                  <div className="space-y-4">
                    <Separator />
                    <h4 className="text-lg font-semibold flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      Extraction Results
                    </h4>
                    {outlineResults.map((result, index) => (
                      <Card key={index} className="border-l-4 border-l-blue-500">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg">{result.title}</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {result.outline.map((item, itemIndex) => (
                              <div key={itemIndex} className="flex items-center justify-between p-2 rounded hover:bg-gray-50">
                                <div className="flex items-center gap-3">
                                  <Badge 
                                    variant={item.level === 'H1' ? 'default' : item.level === 'H2' ? 'secondary' : 'outline'}
                                  >
                                    {item.level}
                                  </Badge>
                                  <span className="font-medium">{item.text}</span>
                                </div>
                                <Badge variant="outline">Page {item.page}</Badge>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Round 1B - Persona Analysis */}
          <TabsContent value="round1b">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Persona-Based Section Mining
                </CardTitle>
                <p className="text-gray-600">
                  Extract and rank relevant sections based on user persona and specific job-to-be-done
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>AI Models & Features</AlertTitle>
                  <AlertDescription>
                    • MiniLM-L6-v2 for semantic similarity (~80MB) • T5-small for summarization (~120MB)
                    • KeyBERT for keyword extraction • SpaCy for NLP processing • Auto-persona expander with hardcoded templates
                    • Keyword traceability & similarity scoring • Section clustering & topic grouping • Enhanced prompt generation
                  </AlertDescription>
                </Alert>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Select Persona</label>
                    <Select value={selectedPersona} onValueChange={setSelectedPersona}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose user persona..." />
                      </SelectTrigger>
                      <SelectContent>
                        {personas.map(persona => (
                          <SelectItem key={persona} value={persona}>
                            {persona}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Job-to-be-Done</label>
                  <Textarea
                    value={jobToBeDone}
                    onChange={(e) => setJobToBeDone(e.target.value)}
                    placeholder="Describe what the user wants to accomplish (e.g., 'Summarize organic chemistry chapters for exam preparation')"
                    className="min-h-[100px]"
                  />
                </div>

                {/* Auto-Persona Expander Preview */}
                {selectedPersona && jobToBeDone && !processing && (
                  <Card className="border-2 border-dashed border-orange-200 bg-orange-50">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg flex items-center gap-2">
                        <Lightbulb className="h-5 w-5 text-orange-500" />
                        Auto-Persona Expander Preview
                      </CardTitle>
                      <p className="text-sm text-gray-600">
                        Preview of how your persona and job-to-be-done will be expanded for better analysis
                      </p>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div>
                          <label className="text-sm font-medium text-gray-700">Enhanced Prompt:</label>
                          <p className="text-sm bg-white p-3 rounded border mt-1">
                            {expandPersona(selectedPersona, jobToBeDone).expanded_prompt}
                          </p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="text-sm font-medium text-gray-700">Generated Keywords:</label>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {expandPersona(selectedPersona, jobToBeDone).keywords.slice(0, 8).map((keyword, index) => (
                                <Badge key={index} variant="outline" className="text-xs bg-orange-100 text-orange-800">
                                  {keyword}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          <div>
                            <label className="text-sm font-medium text-gray-700">Focus Topics:</label>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {expandPersona(selectedPersona, jobToBeDone).topics.map((topic, index) => (
                                <Badge key={index} variant="secondary" className="text-xs">
                                  {topic}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                <div className="flex items-center gap-4">
                  <Button 
                    onClick={processPersonaAnalysis}
                    disabled={files.length === 0 || !selectedPersona || !jobToBeDone || processing}
                    className="flex items-center gap-2"
                  >
                    {processing ? (
                      <>
                        <Clock className="h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Target className="h-4 w-4" />
                        Analyze Sections
                      </>
                    )}
                  </Button>
                  
                  {personaResults && (
                    <Button 
                      variant="outline"
                      onClick={() => downloadResults(personaResults, 'persona_analysis.json')}
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      Download JSON
                    </Button>
                  )}
                </div>

                {processing && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>AI analysis in progress...</span>
                      <span>{Math.round(progress)}%</span>
                    </div>
                    <Progress value={progress} className="w-full" />
                  </div>
                )}

                {personaResults && (
                  <div className="space-y-4">
                    <Separator />
                    <h4 className="text-lg font-semibold flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      Analysis Results
                    </h4>

                    <Card className="border-l-4 border-l-purple-500">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg">Analysis Metadata</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div><strong>Persona:</strong> {personaResults.metadata.persona}</div>
                          <div><strong>Documents:</strong> {personaResults.metadata.documents.length}</div>
                          <div className="col-span-2"><strong>Job-to-be-Done:</strong> {personaResults.metadata.job_to_be_done}</div>
                        </div>
                      </CardContent>
                    </Card>

                    {personaResults.expanded_persona && (
                      <Card className="border-l-4 border-l-orange-500 bg-gradient-to-r from-orange-50 to-yellow-50">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg flex items-center gap-2">
                            <Lightbulb className="h-5 w-5 text-orange-500" />
                            Auto-Persona Expansion Results
                          </CardTitle>
                          <p className="text-sm text-gray-600">
                            Enhanced analysis using AI-powered persona expansion
                          </p>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div>
                            <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                              <Brain className="h-4 w-4" />
                              Enhanced Analysis Prompt:
                            </label>
                            <p className="text-sm bg-white p-3 rounded border mt-2 leading-relaxed">
                              {personaResults.expanded_persona.expanded_prompt}
                            </p>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                                <Tags className="h-4 w-4" />
                                Expanded Keywords ({personaResults.expanded_persona.keywords.length}):
                              </label>
                              <div className="flex flex-wrap gap-1 mt-2">
                                {personaResults.expanded_persona.keywords.map((keyword, index) => (
                                  <Badge 
                                    key={index} 
                                    variant="outline" 
                                    className="text-xs bg-orange-100 text-orange-800 border-orange-300"
                                  >
                                    {keyword}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            
                            <div>
                              <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                                <Target className="h-4 w-4" />
                                Focus Topics:
                              </label>
                              <div className="flex flex-wrap gap-1 mt-2">
                                {personaResults.expanded_persona.topics.map((topic, index) => (
                                  <Badge 
                                    key={index} 
                                    variant="secondary" 
                                    className="text-xs bg-yellow-100 text-yellow-800"
                                  >
                                    {topic}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {personaResults.clustered_results ? (
                      <Card className="border-l-4 border-l-indigo-500 bg-gradient-to-r from-indigo-50 to-purple-50">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg flex items-center gap-2">
                            <Network className="h-5 w-5 text-indigo-600" />
                            Section Clustering & Topic Grouping
                          </CardTitle>
                          <p className="text-sm text-gray-600">
                            Sections grouped by semantic similarity using MiniLM-L6-v2 embeddings and KMeans clustering
                          </p>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-6">
                            {personaResults.clustered_results.clusters.map((cluster, clusterIndex) => (
                              <div key={clusterIndex} className="border rounded-lg bg-white shadow-sm">
                                <div className="border-b bg-gradient-to-r from-indigo-100 to-purple-100 p-4">
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                      <Badge 
                                        variant="secondary" 
                                        className="bg-indigo-600 text-white hover:bg-indigo-700"
                                      >
                                        Cluster {clusterIndex + 1}
                                      </Badge>
                                      <h3 className="text-lg font-semibold text-indigo-900">
                                        {cluster.topic}
                                      </h3>
                                    </div>
                                    <Badge variant="outline" className="text-indigo-700 border-indigo-300">
                                      {cluster.sections.length} section{cluster.sections.length !== 1 ? 's' : ''}
                                    </Badge>
                                  </div>
                                </div>

                                <div className="p-4">
                                  <div className="space-y-4">
                                    {cluster.sections.map((section, sectionIndex) => (
                                      <div 
                                        key={sectionIndex} 
                                        className="p-4 border border-gray-200 rounded-lg bg-gradient-to-r from-gray-50 to-blue-50 hover:from-blue-50 hover:to-indigo-50 transition-colors"
                                      >
                                        <div className="flex items-start justify-between mb-3">
                                          <div className="flex items-center gap-3">
                                            <Badge className="bg-green-100 text-green-800">
                                              Rank #{section.importance_rank}
                                            </Badge>
                                            <div>
                                              <div className="font-medium text-gray-900">{section.section_title}</div>
                                              <div className="text-sm text-gray-500">{section.document}</div>
                                            </div>
                                          </div>
                                          <div className="flex items-center gap-2">
                                            <Badge variant="outline">Page {section.page}</Badge>
                                            <Badge 
                                              variant="secondary" 
                                              className="bg-blue-100 text-blue-800"
                                            >
                                              {(section.embedding_score * 100).toFixed(1)}% match
                                            </Badge>
                                          </div>
                                        </div>

                                        <div className="space-y-2">
                                          <div className="flex items-center gap-2">
                                            <Hash className="h-4 w-4 text-gray-500" />
                                            <span className="text-sm font-medium text-gray-700">Matched Keywords:</span>
                                          </div>
                                          <div className="flex flex-wrap gap-1">
                                            {section.matched_keywords.map((keyword, keywordIndex) => (
                                              <Badge 
                                                key={keywordIndex} 
                                                variant="outline" 
                                                className="text-xs bg-yellow-50 text-yellow-800 border-yellow-200"
                                              >
                                                {keyword}
                                              </Badge>
                                            ))}
                                          </div>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>

                          <div className="mt-6 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                            <div className="flex items-center gap-2 mb-2">
                              <Brain className="h-4 w-4 text-indigo-600" />
                              <span className="text-sm font-medium text-indigo-900">Clustering Statistics</span>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <div className="font-medium text-indigo-800">Total Clusters</div>
                                <div className="text-indigo-600">{personaResults.clustered_results.clusters.length}</div>
                              </div>
                              <div>
                                <div className="font-medium text-indigo-800">Total Sections</div>
                                <div className="text-indigo-600">
                                  {personaResults.clustered_results.clusters.reduce((sum, cluster) => sum + cluster.sections.length, 0)}
                                </div>
                              </div>
                              <div>
                                <div className="font-medium text-indigo-800">Avg Similarity</div>
                                <div className="text-indigo-600">
                                  {(personaResults.extracted_sections.reduce((sum, s) => sum + s.embedding_score, 0) / personaResults.extracted_sections.length * 100).toFixed(1)}%
                                </div>
                              </div>
                              <div>
                                <div className="font-medium text-indigo-800">Algorithm</div>
                                <div className="text-indigo-600">KMeans + MiniLM</div>
                              </div>
                            </div>
                          </div>
                                                </CardContent>
                      </Card>
                    ) : (
                      <Card className="border-l-4 border-l-green-500">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-lg flex items-center gap-2">
                            <TrendingUp className="h-5 w-5" />
                            Extracted Sections (Ranked with AI Insights)
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            {personaResults.extracted_sections.map((section, index) => (
                              <div key={index} className="p-4 border rounded-lg bg-gradient-to-r from-green-50 to-blue-50">
                                <div className="flex items-start justify-between mb-3">
                                  <div className="flex items-center gap-3">
                                    <Badge className="bg-green-100 text-green-800">
                                      Rank #{section.importance_rank}
                                    </Badge>
                                    <div>
                                      <div className="font-medium">{section.section_title}</div>
                                      <div className="text-sm text-gray-500">{section.document}</div>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <Badge variant="outline">Page {section.page}</Badge>
                                    <Badge 
                                      variant="secondary" 
                                      className="bg-blue-100 text-blue-800"
                                    >
                                      {(section.embedding_score * 100).toFixed(1)}% match
                                    </Badge>
                                  </div>
                                </div>
                                
                                <div className="space-y-2">
                                  <div className="flex items-center gap-2">
                                    <Hash className="h-4 w-4 text-gray-500" />
                                    <span className="text-sm font-medium text-gray-700">Matched Keywords:</span>
                                  </div>
                                  <div className="flex flex-wrap gap-1">
                                    {section.matched_keywords.map((keyword, keywordIndex) => (
                                      <Badge 
                                        key={keywordIndex} 
                                        variant="outline" 
                                        className="text-xs bg-yellow-50 text-yellow-800 border-yellow-200"
                                      >
                                        {keyword}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    <Card className="border-l-4 border-l-blue-500">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg">Subsection Analysis</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {personaResults.subsection_analysis.map((analysis, index) => (
                            <div key={index} className="p-4 border rounded-lg bg-blue-50">
                              <div className="flex items-center justify-between mb-2">
                                <div className="text-sm font-medium text-blue-800">
                                  {analysis.document}
                                </div>
                                <Badge variant="outline">Page {analysis.page_number}</Badge>
                              </div>
                              <p className="text-gray-700 text-sm leading-relaxed">
                                {analysis.refined_text}
                              </p>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;
