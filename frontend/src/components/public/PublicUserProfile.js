import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { customUrlsService } from '../../services/customUrlsService';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '../ui/avatar';
import { 
  User, 
  UserCheck, 
  ExternalLink, 
  Twitter, 
  Instagram, 
  Linkedin, 
  Globe,
  Calendar,
  Briefcase,
  Star,
  ArrowRight,
  LogIn
} from 'lucide-react';
import { Loader2 } from 'lucide-react';

const PublicUserProfile = () => {
  const { displayName } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (displayName) {
      loadUserProfile();
    }
  }, [displayName]);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const profileData = await customUrlsService.getPublicUserProfile(displayName);
      
      if (profileData) {
        setProfile(profileData);
      } else {
        setError('User not found');
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
      setError('Failed to load user profile');
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
      day: 'numeric'
    });
  };

  const getSocialIcon = (platform) => {
    switch (platform.toLowerCase()) {
      case 'twitter': return <Twitter className="h-4 w-4" />;
      case 'instagram': return <Instagram className="h-4 w-4" />;
      case 'linkedin': return <Linkedin className="h-4 w-4" />;
      default: return <Globe className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
          <p className="text-[#474545]/70">Loading profile...</p>
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
              <User className="h-12 w-12 mx-auto text-gray-400" />
            </div>
            <h2 className="text-xl font-semibold mb-2">Profile Not Found</h2>
            <p className="text-gray-600 mb-6">
              The user profile "@{displayName}" could not be found.
            </p>
            <div className="space-y-2">
              <Button onClick={handleAppRedirect} className="w-full">
                <ArrowRight className="h-4 w-4 mr-2" />
                Go to f01i.ai
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

  if (!profile) {
    return null;
  }

  const socialLinks = profile.social_links || {};
  const specialties = profile.specialties || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl font-bold text-[#0097B2]">f01i.ai</div>
              <div className="text-gray-400">/</div>
              <div className="text-gray-600">@{profile.display_name}</div>
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
        <Card>
          <CardHeader>
            <div className="flex items-start space-x-6">
              <Avatar className="h-20 w-20">
                <AvatarImage src={profile.avatar_url} alt={profile.display_name} />
                <AvatarFallback className="text-xl">
                  {profile.display_name.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <CardTitle className="text-2xl">{profile.display_name}</CardTitle>
                  {profile.seller_mode && (
                    <Badge variant="secondary" className="flex items-center space-x-1">
                      <UserCheck className="h-3 w-3" />
                      <span>Verified Seller</span>
                    </Badge>
                  )}
                </div>
                
                {profile.bio && (
                  <p className="text-gray-600 mb-4">{profile.bio}</p>
                )}
                
                <div className="flex items-center text-sm text-gray-500 space-x-4">
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>Joined {formatDate(profile.created_at)}</span>
                  </div>
                  
                  {profile.seller_mode && (
                    <div className="flex items-center space-x-1">
                      <Briefcase className="h-4 w-4" />
                      <span>Professional Seller</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </CardHeader>
          
          <CardContent>
            {/* Specialties */}
            {specialties.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">Specialties</h3>
                <div className="flex flex-wrap gap-2">
                  {specialties.map((specialty, index) => (
                    <Badge key={index} variant="outline">
                      {specialty}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            
            {/* Social Links */}
            {Object.keys(socialLinks).length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">Connect</h3>
                <div className="flex flex-wrap gap-3">
                  {Object.entries(socialLinks).map(([platform, url]) => (
                    <a
                      key={platform}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                    >
                      {getSocialIcon(platform)}
                      <span className="text-sm capitalize">{platform}</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  ))}
                </div>
              </div>
            )}
            
            {/* Call to Action */}
            {!user && (
              <div className="bg-gradient-to-r from-[#0097B2] to-[#00B4D8] rounded-lg p-6 text-white">
                <h3 className="text-xl font-semibold mb-2">Join f01i.ai Today</h3>
                <p className="text-blue-100 mb-4">
                  Connect with {profile.display_name} and access AI-powered investment tools, 
                  trading bots, and expert portfolios.
                </p>
                <div className="flex space-x-3">
                  <Button 
                    onClick={handleLoginRedirect}
                    variant="secondary"
                    className="bg-white text-[#0097B2] hover:bg-gray-100"
                  >
                    <LogIn className="h-4 w-4 mr-2" />
                    Sign Up Free
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
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PublicUserProfile;