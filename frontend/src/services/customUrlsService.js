import axios from 'axios';

// Get backend URL from environment
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://url-wizard.preview.emergentagent.com';

class CustomUrlsService {
  constructor() {
    this.baseUrl = `${BACKEND_URL}/api/urls`;
  }

  /**
   * Validate a slug for uniqueness and format
   */
  async validateSlug(slug, excludeUserId = null) {
    try {
      const response = await axios.post(`${this.baseUrl}/validate-slug`, {
        slug: slug,
        exclude_user_id: excludeUserId
      });
      
      return response.data;
    } catch (error) {
      console.error('Error validating slug:', error);
      throw error;
    }
  }

  /**
   * Get reserved words list
   */
  async getReservedWords() {
    try {
      const response = await axios.get(`${this.baseUrl}/reserved-words`);
      return response.data.reserved_words;
    } catch (error) {
      console.error('Error fetching reserved words:', error);
      throw error;
    }
  }

  /**
   * Generate slug from text
   */
  async generateSlug(text) {
    try {
      const response = await axios.post(`${this.baseUrl}/generate-slug?text=${encodeURIComponent(text)}`);
      return response.data;
    } catch (error) {
      console.error('Error generating slug:', error);
      throw error;
    }
  }

  /**
   * Get public user profile by display name
   */
  async getPublicUserProfile(displayName) {
    try {
      const response = await axios.get(`${this.baseUrl}/public/user/${displayName}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        return null; // User not found
      }
      console.error('Error fetching public user profile:', error);
      throw error;
    }
  }

  /**
   * Get public bot details by slug
   */
  async getPublicBot(slug) {
    try {
      const response = await axios.get(`${this.baseUrl}/public/bots/${slug}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        return null; // Bot not found
      }
      console.error('Error fetching public bot:', error);
      throw error;
    }
  }

  /**
   * Get public marketplace product by slug
   */
  async getPublicMarketplaceProduct(slug) {
    try {
      const response = await axios.get(`${this.baseUrl}/public/marketplace/${slug}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        return null; // Product not found
      }
      console.error('Error fetching public marketplace product:', error);
      throw error;
    }
  }

  /**
   * Get public feed post by slug
   */
  async getPublicFeedPost(slug) {
    try {
      const response = await axios.get(`${this.baseUrl}/public/feed/${slug}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        return null; // Post not found
      }
      console.error('Error fetching public feed post:', error);
      throw error;
    }
  }

  /**
   * Update bot slug (authenticated)
   */
  async updateBotSlug(botId, newSlug) {
    try {
      const response = await axios.post(`${this.baseUrl}/update-bot-slug/${botId}?new_slug=${encodeURIComponent(newSlug)}`);
      return response.data;
    } catch (error) {
      console.error('Error updating bot slug:', error);
      throw error;
    }
  }

  /**
   * Update portfolio slug (authenticated)
   */
  async updatePortfolioSlug(portfolioId, newSlug) {
    try {
      const response = await axios.post(`${this.baseUrl}/update-portfolio-slug/${portfolioId}?new_slug=${encodeURIComponent(newSlug)}`);
      return response.data;
    } catch (error) {
      console.error('Error updating portfolio slug:', error);
      throw error;
    }
  }

  /**
   * Generate public URL for user profile
   */
  generateUserProfileUrl(displayName) {
    return `/${displayName}`;
  }

  /**
   * Generate public URL for bot
   */
  generateBotUrl(slug) {
    return `/bots/${slug}`;
  }

  /**
   * Generate public URL for marketplace product
   */
  generateMarketplaceUrl(slug) {
    return `/marketplace/${slug}`;
  }

  /**
   * Generate public URL for feed post
   */
  generateFeedUrl(slug) {
    return `/feed/${slug}`;
  }

  /**
   * Utility: Check if text is a reserved word (client-side check)
   */
  isReservedWord(text, reservedWords = {}) {
    if (!text || !reservedWords) return false;
    
    const lowerText = text.toLowerCase();
    for (const category in reservedWords) {
      const words = reservedWords[category] || [];
      if (words.some(word => word.toLowerCase() === lowerText)) {
        return true;
      }
    }
    return false;
  }

  /**
   * Utility: Generate slug from text (client-side, basic version)
   */
  generateSlugClientSide(text) {
    if (!text || !text.trim()) return '';
    
    return text
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9\s\-_]/g, '') // Remove special characters
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Replace multiple hyphens with single
      .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
  }

  /**
   * Utility: Validate slug format (client-side)
   */
  validateSlugFormat(slug) {
    if (!slug || typeof slug !== 'string') {
      return { valid: false, error: 'Slug cannot be empty' };
    }

    if (slug.length < 3) {
      return { valid: false, error: 'Name must be at least 3 characters long' };
    }

    if (slug.length > 50) {
      return { valid: false, error: 'Name must be no more than 50 characters long' };
    }

    if (!/^[a-zA-Z0-9_-]+$/.test(slug)) {
      return { valid: false, error: 'Only letters, numbers, hyphens, and underscores are allowed' };
    }

    return { valid: true };
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await axios.get(`${this.baseUrl}/health`);
      return response.data;
    } catch (error) {
      console.error('Error checking Custom URLs health:', error);
      throw error;
    }
  }
}

// Export a singleton instance
export const customUrlsService = new CustomUrlsService();

// Also export the class for direct instantiation if needed
export default CustomUrlsService;