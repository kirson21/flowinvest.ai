import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { customUrlsService } from '../../services/customUrlsService';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { 
  FileText, 
  Calendar, 
  Globe, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  ArrowRight,
  LogIn,
  ExternalLink,
  Languages,
  AlertCircle
} from 'lucide-react';
import { Loader2 } from 'lucide-react';

const PublicFeedPost = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (slug) {
      loadPostDetails();
    }
  }, [slug]);

  const loadPostDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const postData = await customUrlsService.getPublicFeedPost(slug);
      
      if (postData) {
        setPost(postData);
      } else {
        setError('Post not found');
      }
    } catch (error) {
      console.error('Error loading post details:', error);
      setError('Failed to load post details');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginRedirect = () => {
    navigate('/login');
  };

  const handleAppRedirect = () => {
    if (user) {
      navigate('/app');
    } else {
      navigate('/login');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
      case 'bullish': 
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'negative':
      case 'bearish': 
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      case 'neutral':
      default: 
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
      case 'bullish': 
        return 'bg-green-100 text-green-800 border-green-200';
      case 'negative':
      case 'bearish': 
        return 'bg-red-100 text-red-800 border-red-200';
      case 'neutral':
      default: 
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getLanguageName = (langCode) => {
    const languages = {
      'en': 'English',
      'es': 'Spanish',
      'fr': 'French',
      'de': 'German',
      'it': 'Italian',
      'pt': 'Portuguese',
      'ja': 'Japanese',
      'ko': 'Korean',
      'zh': 'Chinese',
      'ru': 'Russian',
      'ar': 'Arabic'
    };
    return languages[langCode] || langCode.toUpperCase();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
          <p className="text-[#474545]/70">Loading post...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <div className="mb-4">
              <FileText className="h-12 w-12 mx-auto text-gray-400" />
            </div>
            <h2 className="text-xl font-semibold mb-2">Post Not Found</h2>
            <p className="text-gray-600 mb-6">
              The post "{slug}" could not be found or is not publicly available.
            </p>
            <div className="space-y-2">
              <Button onClick={handleAppRedirect} className="w-full">
                <ArrowRight className="h-4 w-4 mr-2" />
                Browse Feed
              </Button>
              {!user && (
                <Button onClick={handleLoginRedirect} variant="outline" className="w-full">
                  <LogIn className="h-4 w-4 mr-2" />
                  Login / Register
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!post) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl font-bold text-[#0097B2]">f01i.ai</div>
              <div className="text-gray-400">/</div>
              <div className="text-gray-600">feed</div>
              <div className="text-gray-400">/</div>
              <div className="text-gray-600 truncate max-w-xs">{post.title}</div>
            </div>
            <div className="flex items-center space-x-2">
              {user ? (
                <Button onClick={handleAppRedirect} variant="outline">
                  <ArrowRight className="h-4 w-4 mr-2" />
                  Go to App
                </Button>
              ) : (
                <>
                  <Button onClick={handleLoginRedirect} variant="outline">
                    <LogIn className="h-4 w-4 mr-2" />
                    Login
                  </Button>
                  <Button onClick={handleAppRedirect}>
                    Get Started
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto p-4 py-8">
        <article>
          <Card>
            <CardHeader>
              <div className="space-y-4">
                {/* Title */}
                <CardTitle className="text-3xl leading-tight">{post.title}</CardTitle>
                
                {/* Meta Information */}
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>
                      {formatDate(post.published_at || post.created_at)}
                    </span>
                  </div>
                  
                  {post.source && (
                    <div className="flex items-center space-x-1">
                      <Globe className="h-4 w-4" />
                      <span>{post.source}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center space-x-1">
                    <Languages className="h-4 w-4" />
                    <span>{getLanguageName(post.language)}</span>
                  </div>
                </div>
                
                {/* Tags/Badges */}
                <div className="flex flex-wrap items-center gap-2">
                  {post.sentiment && (
                    <Badge 
                      variant="outline" 
                      className={`flex items-center space-x-1 ${getSentimentColor(post.sentiment)}`}
                    >
                      {getSentimentIcon(post.sentiment)}
                      <span className="capitalize">{post.sentiment}</span>
                    </Badge>
                  )}
                  
                  {post.language !== 'en' && (
                    <Badge variant="secondary" className="flex items-center space-x-1">
                      <Languages className="h-3 w-3" />
                      <span>Translated</span>
                    </Badge>
                  )}
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-6">
                {/* Summary */}
                {post.summary && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold mb-2 flex items-center space-x-2">
                      <AlertCircle className="h-5 w-5 text-blue-600" />
                      <span>Summary</span>
                    </h3>
                    <p className="text-gray-700 leading-relaxed">{post.summary}</p>
                  </div>
                )}
                
                {/* Content */}
                {post.content && (
                  <div className="prose prose-lg max-w-none">
                    <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                      {post.content}
                    </div>
                  </div>
                )}
                
                {/* If no content, show message */}
                {!post.content && !post.summary && (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="h-12 w-12 mx-auto mb-4" />
                    <p>Full content is available in the f01i.ai app.</p>
                  </div>
                )}
                
                {/* Source Link */}
                {post.source && (
                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-gray-600">
                        Source: {post.source}
                      </div>
                      <Button 
                        onClick={handleAppRedirect}
                        variant="outline" 
                        size="sm"
                      >
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Read More
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
          
          {/* Call to Action for non-authenticated users */}
          {!user && (
            <Card className="mt-6">
              <CardContent className="pt-6">
                <div className="bg-gradient-to-r from-[#0097B2] to-[#00B4D8] rounded-lg p-6 text-white text-center">
                  <h3 className="text-xl font-semibold mb-2">Stay Updated with f01i.ai</h3>
                  <p className="text-blue-100 mb-4">
                    Get real-time AI-powered market insights, trading signals, and investment analysis delivered to your feed.
                  </p>
                  <div className="flex justify-center space-x-3">
                    <Button 
                      onClick={handleLoginRedirect}
                      variant="secondary"
                      className="bg-white text-[#0097B2] hover:bg-gray-100"
                    >
                      <LogIn className="h-4 w-4 mr-2" />
                      Join Free
                    </Button>
                    <Button 
                      onClick={handleAppRedirect}
                      variant="outline"
                      className="border-white text-white hover:bg-white/10"
                    >
                      Learn More
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </article>
      </div>
    </div>
  );
};

export default PublicFeedPost;