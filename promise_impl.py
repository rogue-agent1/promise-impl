#!/usr/bin/env python3
"""Promise/Future implementation from scratch."""
import sys,threading,time
class Promise:
    def __init__(self,executor=None):
        self._state='pending';self._value=None;self._callbacks=[];self._lock=threading.Lock()
        if executor:
            try: executor(self._resolve,self._reject)
            except Exception as e: self._reject(e)
    def _resolve(self,value):
        with self._lock:
            if self._state!='pending': return
            self._state='fulfilled';self._value=value
            for cb,_ in self._callbacks: cb(value)
    def _reject(self,reason):
        with self._lock:
            if self._state!='pending': return
            self._state='rejected';self._value=reason
            for _,cb in self._callbacks:
                if cb: cb(reason)
    def then(self,on_fulfilled,on_rejected=None):
        p=Promise()
        def handle_fulfilled(v):
            try: result=on_fulfilled(v);p._resolve(result)
            except Exception as e: p._reject(e)
        def handle_rejected(r):
            if on_rejected:
                try: result=on_rejected(r);p._resolve(result)
                except Exception as e: p._reject(e)
            else: p._reject(r)
        with self._lock:
            if self._state=='fulfilled': handle_fulfilled(self._value)
            elif self._state=='rejected': handle_rejected(self._value)
            else: self._callbacks.append((handle_fulfilled,handle_rejected))
        return p
    @staticmethod
    def all(promises):
        results=[None]*len(promises);count=[0]
        p=Promise()
        for i,pr in enumerate(promises):
            def cb(v,idx=i):
                results[idx]=v;count[0]+=1
                if count[0]==len(promises): p._resolve(results)
            pr.then(cb,p._reject)
        return p
def main():
    # Sync demo
    p=Promise(lambda resolve,reject: resolve(42))
    p.then(lambda v: print(f"Resolved: {v}"))
    # Chain
    Promise(lambda res,rej: res(10)).then(lambda v: v*2).then(lambda v: print(f"Chained: {v}"))
    # All
    ps=[Promise(lambda res,rej,i=i: res(i*10)) for i in range(3)]
    Promise.all(ps).then(lambda v: print(f"All: {v}"))
    # Error
    Promise(lambda res,rej: rej(ValueError("oops"))).then(lambda v: v, lambda e: print(f"Caught: {e}"))
if __name__=="__main__": main()
