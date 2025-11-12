/**
 * Serviço de persistência de sessão
 * Gerencia localStorage e cookies de forma sincronizada
 */

const TOKEN_KEY = 'token';
const USER_KEY = 'user';
const TOKEN_EXPIRY_KEY = 'token_expiry';

export const sessionStorage = {
  /**
   * Salva o token e dados do usuário
   */
  saveSession(token: string, user: any, expiresIn: number = 60 * 60 * 24 * 7) {
    if (typeof window === 'undefined') return;
    
    try {
      // Salvar no localStorage
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      
      // Calcular tempo de expiração
      const expiryTime = Date.now() + (expiresIn * 1000);
      localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());
      
      // Salvar no cookie também
      document.cookie = `${TOKEN_KEY}=${token}; path=/; max-age=${expiresIn}; SameSite=Lax`;
      
      console.log('[SessionStorage] Sessão salva com sucesso', {
        user: user?.nome || user?.email,
        expiresIn: `${expiresIn}s`,
        expiryDate: new Date(expiryTime).toLocaleString()
      });
    } catch (error) {
      console.error('[SessionStorage] Erro ao salvar sessão:', error);
    }
  },

  /**
   * Recupera o token salvo
   */
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      
      if (!token) {
        return null;
      }
      
      // Verificar se o token expirou
      if (this.isTokenExpired()) {
        console.warn('[SessionStorage] Token expirado, limpando sessão');
        this.clearSession();
        return null;
      }
      
      return token;
    } catch (error) {
      console.error('[SessionStorage] Erro ao recuperar token:', error);
      return null;
    }
  },

  /**
   * Recupera os dados do usuário salvos
   */
  getUser(): any | null {
    if (typeof window === 'undefined') return null;
    
    try {
      const userStr = localStorage.getItem(USER_KEY);
      if (!userStr) return null;
      
      return JSON.parse(userStr);
    } catch (error) {
      console.error('[SessionStorage] Erro ao recuperar usuário:', error);
      return null;
    }
  },

  /**
   * Verifica se o token está expirado
   */
  isTokenExpired(): boolean {
    if (typeof window === 'undefined') return true;
    
    try {
      const expiryStr = localStorage.getItem(TOKEN_EXPIRY_KEY);
      if (!expiryStr) return true;
      
      const expiryTime = parseInt(expiryStr, 10);
      const now = Date.now();
      
      // Considerar expirado se faltar menos de 5 minutos
      const BUFFER_TIME = 5 * 60 * 1000; // 5 minutos
      return now >= (expiryTime - BUFFER_TIME);
    } catch (error) {
      console.error('[SessionStorage] Erro ao verificar expiração:', error);
      return true;
    }
  },

  /**
   * Limpa a sessão completamente
   */
  clearSession() {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      localStorage.removeItem(TOKEN_EXPIRY_KEY);
      document.cookie = `${TOKEN_KEY}=; path=/; max-age=0`;
      
      console.log('[SessionStorage] Sessão limpa com sucesso');
    } catch (error) {
      console.error('[SessionStorage] Erro ao limpar sessão:', error);
    }
  },

  /**
   * Verifica se há uma sessão válida
   */
  hasValidSession(): boolean {
    return !!(this.getToken() && this.getUser() && !this.isTokenExpired());
  },

  /**
   * Obtém tempo restante da sessão em segundos
   */
  getTimeRemaining(): number {
    if (typeof window === 'undefined') return 0;
    
    try {
      const expiryStr = localStorage.getItem(TOKEN_EXPIRY_KEY);
      if (!expiryStr) return 0;
      
      const expiryTime = parseInt(expiryStr, 10);
      const now = Date.now();
      const remaining = Math.max(0, Math.floor((expiryTime - now) / 1000));
      
      return remaining;
    } catch (error) {
      return 0;
    }
  }
};
