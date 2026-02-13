"""
OTP (One-Time Password) and Magic Link Reader for Specter

Reads verification codes and magic links from real email inboxes via IMAP.
Supports Gmail, Outlook, and other IMAP-compatible email providers.
"""

import asyncio
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime
from typing import Dict, Any, Optional
import os
from concurrent.futures import ThreadPoolExecutor


class OTPReader:
    """Reads OTP codes from real email inboxes via IMAP."""
    
    def __init__(self, email_address: str, app_password: str, imap_server: str = "imap.gmail.com"):
        """
        Initialize OTP reader.
        
        Args:
            email_address: Email address to read from
            app_password: App-specific password (not regular password)
            imap_server: IMAP server address (default: Gmail)
        """
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = imap_server
        self.executor = ThreadPoolExecutor(max_workers=1)
    
    async def wait_for_otp(
        self,
        sender_filter: Optional[str] = None,
        since_timestamp: Optional[datetime] = None,
        otp_pattern: str = r'\b\d{4,8}\b',
        timeout_seconds: int = 60,
        poll_interval: int = 3
    ) -> Dict[str, Any]:
        """
        Wait for OTP code to arrive in email.
        
        Returns:
            {
                "found": bool,
                "code": str or None,
                "method": "email_imap",
                "wait_time_ms": int,
                "email_subject": str,
                "error": str or None
            }
        """
        start_time = datetime.now()
        elapsed_ms = 0
        
        # Use test start time if not provided
        if not since_timestamp:
            since_timestamp = start_time
        
        while elapsed_ms < (timeout_seconds * 1000):
            try:
                # Run IMAP operations in executor to avoid blocking
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._fetch_otp_sync,
                    sender_filter,
                    since_timestamp,
                    otp_pattern
                )
                
                if result['found']:
                    elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                    return {
                        "found": True,
                        "code": result['code'],
                        "method": "email_imap",
                        "wait_time_ms": elapsed_ms,
                        "email_subject": result.get('subject', ''),
                        "error": None
                    }
                
            except Exception as e:
                print(f"OTP fetch error: {e}")
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Timeout reached
        return {
            "found": False,
            "code": None,
            "method": "email_imap",
            "wait_time_ms": elapsed_ms,
            "email_subject": "",
            "error": "Timeout: No OTP received"
        }
    
    def _fetch_otp_sync(
        self,
        sender_filter: Optional[str],
        since_timestamp: datetime,
        otp_pattern: str
    ) -> Dict[str, Any]:
        """Synchronous IMAP operations (runs in executor)."""
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_address, self.app_password)
            mail.select('INBOX')
            
            # Build search criteria
            # Search for emails after the test started
            date_str = since_timestamp.strftime("%d-%b-%Y")
            search_criteria = f'(SINCE {date_str})'
            
            if sender_filter:
                search_criteria = f'{search_criteria} (FROM "{sender_filter}")'
            
            # Search for emails
            status, messages = mail.search(None, search_criteria)
            if status != 'OK':
                mail.close()
                mail.logout()
                return {"found": False}
            
            email_ids = messages[0].split()
            
            # Process emails in reverse order (newest first)
            for email_id in reversed(email_ids):
                try:
                    # Fetch email
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Check if email is recent enough (SINCE only checks date, not time)
                    email_date = email.utils.parsedate_to_datetime(msg['Date'])
                    if email_date < since_timestamp:
                        continue
                    
                    # Extract subject
                    subject = self._decode_header(msg['Subject'])
                    
                    # Extract body
                    body = self._get_email_body(msg)
                    
                    # Search for OTP code
                    matches = re.findall(otp_pattern, body)
                    if matches:
                        # Return first match
                        code = matches[0]
                        
                        # Mark as read
                        mail.store(email_id, '+FLAGS', '\\Seen')
                        
                        mail.close()
                        mail.logout()
                        
                        return {
                            "found": True,
                            "code": code,
                            "subject": subject
                        }
                
                except Exception as e:
                    print(f"Error processing email: {e}")
                    continue
            
            mail.close()
            mail.logout()
            return {"found": False}
            
        except Exception as e:
            print(f"IMAP error: {e}")
            return {"found": False}
    
    async def wait_for_magic_link(
        self,
        sender_filter: Optional[str] = None,
        since_timestamp: Optional[datetime] = None,
        link_pattern: str = r'https?://\S+verify\S+|https?://\S+confirm\S+',
        timeout_seconds: int = 60
    ) -> Dict[str, Any]:
        """
        Wait for magic link to arrive in email.
        
        Returns:
            {
                "found": bool,
                "link": str or None,
                "wait_time_ms": int,
                "error": str or None
            }
        """
        start_time = datetime.now()
        elapsed_ms = 0
        
        if not since_timestamp:
            since_timestamp = start_time
        
        while elapsed_ms < (timeout_seconds * 1000):
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._fetch_magic_link_sync,
                    sender_filter,
                    since_timestamp,
                    link_pattern
                )
                
                if result['found']:
                    elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                    return {
                        "found": True,
                        "link": result['link'],
                        "wait_time_ms": elapsed_ms,
                        "error": None
                    }
                
            except Exception as e:
                print(f"Magic link fetch error: {e}")
            
            await asyncio.sleep(3)
            elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            "found": False,
            "link": None,
            "wait_time_ms": elapsed_ms,
            "error": "Timeout: No magic link received"
        }
    
    def _fetch_magic_link_sync(
        self,
        sender_filter: Optional[str],
        since_timestamp: datetime,
        link_pattern: str
    ) -> Dict[str, Any]:
        """Synchronous magic link fetch (runs in executor)."""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_address, self.app_password)
            mail.select('INBOX')
            
            date_str = since_timestamp.strftime("%d-%b-%Y")
            search_criteria = f'(SINCE {date_str})'
            
            if sender_filter:
                search_criteria = f'{search_criteria} (FROM "{sender_filter}")'
            
            status, messages = mail.search(None, search_criteria)
            if status != 'OK':
                mail.close()
                mail.logout()
                return {"found": False}
            
            email_ids = messages[0].split()
            
            for email_id in reversed(email_ids):
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    email_date = email.utils.parsedate_to_datetime(msg['Date'])
                    if email_date < since_timestamp:
                        continue
                    
                    body = self._get_email_body(msg)
                    
                    # Search for magic link
                    matches = re.findall(link_pattern, body)
                    if matches:
                        link = matches[0]
                        
                        # Mark as read
                        mail.store(email_id, '+FLAGS', '\\Seen')
                        
                        mail.close()
                        mail.logout()
                        
                        return {
                            "found": True,
                            "link": link
                        }
                
                except Exception as e:
                    print(f"Error processing email: {e}")
                    continue
            
            mail.close()
            mail.logout()
            return {"found": False}
            
        except Exception as e:
            print(f"IMAP error: {e}")
            return {"found": False}
    
    def _get_email_body(self, msg) -> str:
        """Extract email body from multipart message."""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
                elif content_type == "text/html":
                    try:
                        html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Basic HTML tag stripping
                        body += re.sub(r'<[^>]+>', ' ', html_body)
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
        
        return body
    
    def _decode_header(self, header_value) -> str:
        """Decode email header."""
        if not header_value:
            return ""
        
        decoded = decode_header(header_value)
        header_text = ""
        
        for text, charset in decoded:
            if isinstance(text, bytes):
                try:
                    header_text += text.decode(charset or 'utf-8', errors='ignore')
                except:
                    header_text += text.decode('utf-8', errors='ignore')
            else:
                header_text += text
        
        return header_text
