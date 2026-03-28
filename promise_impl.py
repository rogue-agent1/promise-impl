#!/usr/bin/env python3
"""promise_impl - Promise/Future pattern implementation."""
import sys,threading,time
class Promise:
    def __init__(s,executor=None):
        s._value=None;s._error=None;s._state="pending";s._callbacks=[];s._lock=threading.Lock();s._event=threading.Event()
        if executor:threading.Thread(target=lambda:executor(s.resolve,s.reject),daemon=True).start()
    def resolve(s,value):
        with s._lock:
            if s._state!="pending":return
            s._value=value;s._state="fulfilled";s._event.set()
        for cb in s._callbacks:cb(value)
    def reject(s,error):
        with s._lock:
            if s._state!="pending":return
            s._error=error;s._state="rejected";s._event.set()
    def then(s,on_fulfilled):
        p=Promise()
        def callback(val):
            try:result=on_fulfilled(val);p.resolve(result)
            except Exception as e:p.reject(e)
        if s._state=="fulfilled":callback(s._value)
        else:s._callbacks.append(callback)
        return p
    def wait(s,timeout=None):s._event.wait(timeout);return s._value if s._state=="fulfilled" else s._error
    @staticmethod
    def all(promises):
        results=[None]*len(promises);done=[0];p=Promise();lock=threading.Lock()
        for i,pr in enumerate(promises):
            def cb(val,idx=i):
                with lock:results[idx]=val;done[0]+=1
                if done[0]==len(promises):p.resolve(results)
            pr.then(cb)
        return p
if __name__=="__main__":
    def async_task(resolve,reject):time.sleep(0.1);resolve(42)
    p=Promise(async_task);result=p.wait(timeout=1);print(f"Result: {result}")
    p2=p.then(lambda x:x*2);time.sleep(0.2);print(f"Chained: {p2._value}")
    promises=[Promise(lambda res,rej,i=i:res(i**2) or None) for i in range(5)]
    all_p=Promise.all(promises);time.sleep(0.5);print(f"All: {all_p._value}")
